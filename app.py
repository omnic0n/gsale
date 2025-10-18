from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm, ButtonForm, ReturnItemForm, CityReportForm, NeighborhoodForm, NeighborhoodReportForm
from upload_function import *
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote
import random, os, math
import hashlib
import json
import requests
import threading
import time
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
except ImportError:
    # Google OAuth libraries not available
    id_token = None
    google_requests = None

import get_data, set_data
import files
import function
import config
import requests
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session functionality

# Initialize the extension
try:
    app.config.from_object("config.ProductionConfig")
except Exception as e:
    print("Warning: Could not load ProductionConfig, using default config: {}".format(e))
    # Set default configuration
    app.config['GOOGLE_MAPS_API_KEY'] = "YOUR_GOOGLE_MAPS_API_KEY"

# Initialize MySQL with proper error handling
try:
    mysql = MySQL(app)
    print("MySQL connection initialized successfully")
    # Set the MySQL connection in get_data and set_data modules
    get_data.set_mysql_connection(mysql)
    set_data.set_mysql_connection(mysql)
except Exception as e:
    print("Error initializing MySQL: {}".format(e))
    mysql = None

# Simple report caching
report_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(report_type, params):
    """Generate cache key for reports"""
    param_str = json.dumps(params, sort_keys=True)
    return "{}_{}".format(report_type, hashlib.md5(param_str.encode()).hexdigest())

def get_cached_report(report_type, params):
    """Get cached report data if available and not expired"""
    cache_key = get_cache_key(report_type, params)
    if cache_key in report_cache:
        timestamp, data = report_cache[cache_key]
        if datetime.now().timestamp() - timestamp < CACHE_DURATION:
            return data
        else:
            del report_cache[cache_key]
    return None

def cache_report(report_type, params, data):
    """Cache report data with timestamp"""
    cache_key = get_cache_key(report_type, params)
    report_cache[cache_key] = (datetime.now().timestamp(), data)

def login_required(f):
    """Decorator to check if user is logged in and redirect to login with next parameter"""
    def decorated_function(*args, **kwargs):
        if not 'loggedin' in session:
            # Don't redirect to login if already on login page
            if request.endpoint != 'login':
                next_page = request.path
                if request.query_string:
                    next_page += '?' + request.query_string.decode('utf-8')
                return redirect(url_for('login', next=next_page))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """Decorator to check if user is logged in and is an admin"""
    def decorated_function(*args, **kwargs):
        if not 'loggedin' in session:
            # Don't redirect to login if already on login page
            if request.endpoint != 'login':
                next_page = request.path
                if request.query_string:
                    next_page += '?' + request.query_string.decode('utf-8')
                return redirect(url_for('login', next=next_page))
        
        # Check if user is admin
        current_user_id = session.get('id')
        if not current_user_id:
            flash('Access denied. Please log in.', 'error')
            return redirect(url_for('index'))
        
        # Check admin status in database
        admin_status = get_data.check_admin_status(current_user_id)
        if not admin_status:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# eBay OAuth 2.0 Functions
def get_ebay_oauth_url():
    """
    Generate eBay OAuth authorization URL
    """
    try:
        # Generate state parameter for security
        state = hashlib.sha256(os.urandom(32)).hexdigest()
        session['ebay_oauth_state'] = state
        
        # Debug: Print state generation
        
        # Determine environment URLs
        if app.config.get('EBAY_SANDBOX_MODE', False):
            auth_url = 'https://auth.sandbox.ebay.com/oauth2/authorize'
        else:
            auth_url = 'https://auth.ebay.com/oauth2/authorize'
        
        # Build authorization URL
        auth_params = {
            'client_id': app.config['EBAY_CLIENT_ID'],
            'response_type': 'code',
            'redirect_uri': app.config['EBAY_REDIRECT_URI'],
            'scope': app.config['EBAY_OAUTH_SCOPE'],
            'state': state
        }
        
        # Debug: Print parameters for troubleshooting
        print(f"  Client ID: {auth_params['client_id']}")
        print(f"  Redirect URI: {auth_params['redirect_uri']}")
        print(f"  Scope: {auth_params['scope'][:100]}...")
        print(f"  State: {auth_params['state']}")
        
        # Create URL with parameters (URL encode the scope)
        from urllib.parse import urlencode
        param_string = urlencode(auth_params)
        full_auth_url = f"{auth_url}?{param_string}"
        
        
        return {
            'success': True,
            'auth_url': full_auth_url,
            'state': state
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to generate OAuth URL: {str(e)}'
        }

def exchange_ebay_code_for_token(authorization_code):
    """
    Exchange authorization code for access token
    """
    try:
        # Determine environment URLs
        if app.config.get('EBAY_SANDBOX_MODE', False):
            token_url = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
        else:
            token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        
        # Prepare token request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {get_ebay_basic_auth()}"
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': app.config['EBAY_REDIRECT_URI']
        }
        
        # Make token request
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))
            
            # Store tokens in session (for immediate use)
            session['ebay_access_token'] = token_data.get('access_token')
            session['ebay_refresh_token'] = token_data.get('refresh_token')
            session['ebay_token_expires'] = expires_at
            
            # Store tokens in database (for persistence and background refresh)
            store_ebay_tokens_in_db(
                token_data.get('access_token'),
                token_data.get('refresh_token'),
                expires_at
            )
            
            # Debug: Print token storage
            
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            }
        else:
            return {
                'success': False,
                'error': f'Token exchange failed: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Token exchange error: {str(e)}'
        }

def refresh_ebay_token(refresh_token):
    """
    Refresh eBay access token using refresh token
    """
    try:
        # Determine environment URLs
        if app.config.get('EBAY_SANDBOX_MODE', False):
            token_url = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
        else:
            token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        
        # Prepare refresh request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {get_ebay_basic_auth()}"
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': app.config['EBAY_OAUTH_SCOPE']
        }
        
        # Make refresh request
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))
            
            # Update session tokens
            session['ebay_access_token'] = token_data.get('access_token')
            if token_data.get('refresh_token'):
                session['ebay_refresh_token'] = token_data.get('refresh_token')
            session['ebay_token_expires'] = expires_at
            
            # Update database tokens
            store_ebay_tokens_in_db(
                token_data.get('access_token'),
                token_data.get('refresh_token', refresh_token),  # Use old refresh token if new one not provided
                expires_at
            )
            
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in')
            }
        else:
            return {
                'success': False,
                'error': f'Token refresh failed: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Token refresh error: {str(e)}'
        }

def get_ebay_basic_auth():
    """
    Generate Basic Auth header for eBay OAuth
    """
    import base64
    credentials = f"{app.config['EBAY_CLIENT_ID']}:{app.config['EBAY_CLIENT_SECRET']}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return encoded_credentials

def get_valid_ebay_token():
    """
    Get a valid eBay access token, automatically refreshing if necessary
    """
    try:
        # First check session tokens
        access_token = session.get('ebay_access_token')
        refresh_token = session.get('ebay_refresh_token')
        token_expires = session.get('ebay_token_expires')
        
        # If no session tokens, try to get from database
        if not access_token:
            db_tokens = get_ebay_tokens_from_db()
            if db_tokens:
                access_token = db_tokens['access_token']
                refresh_token = db_tokens['refresh_token']
                token_expires = db_tokens['expires_at']
                
                # Restore to session for immediate use
                session['ebay_access_token'] = access_token
                session['ebay_refresh_token'] = refresh_token
                session['ebay_token_expires'] = token_expires
        
        if not access_token:
            return {
                'success': False,
                'error': 'No eBay access token found. Please authenticate first.',
                'needs_auth': True
            }
        
        # Check if this is a legacy token format (starts with v^)
        if access_token.startswith('v^'):
            return {
                'success': True,
                'access_token': access_token,
                'is_legacy': True
            }
        
        # Check if token is expired or will expire soon (with 10-minute buffer for safety)
        if token_expires and datetime.now() >= (token_expires - timedelta(minutes=10)):
            if refresh_token:
                # Try to refresh the token
                refresh_result = refresh_ebay_token(refresh_token)
                if refresh_result['success']:
                    return {
                        'success': True,
                        'access_token': refresh_result['access_token']
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Token refresh failed: {refresh_result["error"]}',
                        'needs_auth': True
                    }
            else:
                return {
                    'success': False,
                    'error': 'Token expired and no refresh token available. Please authenticate again.',
                    'needs_auth': True
                }
        
        return {
            'success': True,
            'access_token': access_token
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Token validation error: {str(e)}',
            'needs_auth': True
        }

# Enhanced Token Management System
def store_ebay_tokens_in_db(access_token, refresh_token, expires_at, user_id=None):
    """
    Store eBay tokens in database for persistence across sessions
    """
    try:
        # Ensure MySQL connection is available
        if not mysql.connection:
            try:
                mysql.connect()
            except Exception as conn_error:
                return False
        
        cur = mysql.connection.cursor()
        
        # Use session user ID if not provided
        if not user_id:
            user_id = session.get('id')
        
        if not user_id:
            return False
        
        # Insert or update tokens for this user
        cur.execute("""
            INSERT INTO ebay_tokens (user_id, access_token, refresh_token, expires_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
            access_token = VALUES(access_token),
            refresh_token = VALUES(refresh_token),
            expires_at = VALUES(expires_at),
            updated_at = NOW()
        """, (user_id, access_token, refresh_token, expires_at))
        
        mysql.connection.commit()
        return True
        
    except Exception as e:
        return False

def get_ebay_tokens_from_db(user_id=None):
    """
    Retrieve eBay tokens from database for a specific user
    """
    try:
        # Ensure MySQL connection is available
        if not mysql.connection:
            try:
                mysql.connect()
            except Exception as conn_error:
                return None
        
        cur = mysql.connection.cursor()
        
        # Use session user ID if not provided
        if not user_id:
            user_id = session.get('id')
        
        if not user_id:
            return None
        
        cur.execute("""
            SELECT access_token, refresh_token, expires_at, user_id
            FROM ebay_tokens
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        result = cur.fetchone()
        if result:
            # Handle both dict and tuple formats
            if isinstance(result, dict):
                return {
                    'access_token': result.get('access_token'),
                    'refresh_token': result.get('refresh_token'),
                    'expires_at': result.get('expires_at'),
                    'user_id': result.get('user_id')
                }
            else:
                return {
                    'access_token': result[0],
                    'refresh_token': result[1],
                    'expires_at': result[2],
                    'user_id': result[3] if len(result) > 3 else None
                }
        
        return None
        
    except Exception as e:
        return None

def refresh_token_if_needed():
    """
    Check if token needs refresh and refresh it if necessary
    """
    try:
        # Get tokens from database
        db_tokens = get_ebay_tokens_from_db()
        
        if not db_tokens or not db_tokens.get('refresh_token'):
            return False
        
        # Check if token expires within the next 30 minutes
        expires_at = db_tokens.get('expires_at')
        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            
            # If token expires within 30 minutes, refresh it
            if expires_at <= datetime.now() + timedelta(minutes=30):
                refresh_result = refresh_ebay_token(db_tokens['refresh_token'])
                return refresh_result['success']
        
        return True  # Token is still valid
        
    except Exception as e:
        return False

# eBay API Functions
def get_ebay_active_listings():
    """
    Fetch active listings from eBay API using OAuth 2.0 or legacy token
    """
    try:
        # First try to get OAuth token
        token_result = get_valid_ebay_token()
        
        if token_result['success']:
            # Use OAuth 2.0 token
            api_base_url = app.config.get('EBAY_API_BASE_URL', 'https://api.ebay.com')
            return get_ebay_listings_oauth(token_result['access_token'], api_base_url)
        elif token_result.get('needs_auth'):
            # OAuth token not available, try legacy token
            user_token = app.config.get('EBAY_USER_TOKEN')
            api_base_url = app.config.get('EBAY_API_BASE_URL', 'https://api.ebay.com')
            
            if not user_token or user_token == 'YOUR_EBAY_USER_TOKEN_HERE':
                return {
                    'success': False,
                    'error': 'eBay authentication required. Please authenticate with eBay OAuth or configure a legacy token.',
                    'needs_oauth': True
                }
            
            # Check if this is a legacy token format
            if user_token.startswith('v^'):
                # Try legacy Trading API first for completed/sold items
                legacy_result = get_ebay_completed_listings_legacy(user_token)
                if legacy_result['success']:
                    return legacy_result
                
                # Fallback to Browse API for active listings
                browse_result = get_ebay_recently_sold_items(user_token, api_base_url)
                if browse_result['success']:
                    return browse_result
                
                # Final fallback to legacy Trading API
                return get_ebay_listings_legacy(user_token)
            else:
                # Use modern OAuth 2.0 APIs with legacy token
                return get_ebay_listings_modern(user_token, api_base_url)
        else:
            return {
                'success': False,
                'error': token_result['error']
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': 'Network error: {}'.format(str(e))
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Unexpected error: {}'.format(str(e))
        }

def get_ebay_completed_listings_legacy(user_token):
    """
    Fetch completed/sold listings using eBay Transaction API for accurate financial data
    """
    try:
        import xml.etree.ElementTree as ET
        
        # First get sold listings to get item IDs
        sold_items = get_sold_items_basic(user_token)
        if not sold_items['success']:
            return sold_items
        
        # Then get detailed transaction data for each item
        detailed_listings = []
        for item in sold_items['items']:
            transaction_data = get_item_transaction_details(user_token, item['itemId'])
            if transaction_data['success']:
                # Merge basic item info with detailed transaction data
                detailed_listing = {**item, **transaction_data['transaction_data']}
                detailed_listings.append(detailed_listing)
            else:
                # Fallback to basic item if transaction details fail
                detailed_listings.append(item)
        
        return {
            'success': True,
            'listings': detailed_listings,
            'total': len(detailed_listings),
            'note': 'Using eBay Transaction API for accurate financial data'
        }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Transaction API error: {}'.format(str(e))
        }

def get_sold_items_basic(user_token):
    """
    Get basic sold items list using GetMyeBaySelling
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = "https://api.ebay.com/ws/api.dll"
        
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <SoldList>
                <Include>true</Include>
                <Pagination>
                    <EntriesPerPage>100</EntriesPerPage>
                    <PageNumber>1</PageNumber>
                </Pagination>
            </SoldList>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetMyeBaySellingRequest>""".format(user_token)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': 'eBay API error: {}'.format(error_msg.text)
                    }
            
            # Extract basic item info
            items = []
            sold_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}SoldList')
            if sold_list is not None:
                item_elements = sold_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                for item in item_elements:
                    item_id = item.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                    title = item.find('.//{urn:ebay:apis:eBLBaseComponents}Title')
                    condition = item.find('.//{urn:ebay:apis:eBLBaseComponents}ConditionDisplayName')
                    quantity = item.find('.//{urn:ebay:apis:eBLBaseComponents}Quantity')
                    end_time = item.find('.//{urn:ebay:apis:eBLBaseComponents}EndTime')
                    
                    items.append({
                        'itemId': item_id.text if item_id is not None else 'N/A',
                        'title': title.text if title is not None else 'N/A',
                        'description': title.text if title is not None else 'N/A',
                        'condition': condition.text if condition is not None else 'N/A',
                        'quantity': int(quantity.text) if quantity is not None and quantity.text else 0,
                        'sku': item_id.text if item_id is not None else 'N/A',
                        'end_time': end_time.text if end_time is not None else 'N/A',
                        'status': 'Sold',
                        'ebay_url': 'https://www.ebay.com/itm/{}'.format(item_id.text) if item_id is not None else '#'
                    })
            
            return {
                'success': True,
                'items': items
            }
        else:
            return {
                'success': False,
                'error': 'API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'API error: {}'.format(str(e))
        }

def get_item_transaction_details(user_token, item_id):
    """
    Get detailed transaction information including fees using modern eBay Order API with TAX_BREAKDOWN
    """
    try:
        
        # Check if token is OAuth 2.0 (starts with 'v1.1#' or 'v^1.1#') or legacy
        is_oauth_token = user_token.startswith('v1.1#') or user_token.startswith('v^1.1#')
        
        # Only try modern Order API if we have an OAuth 2.0 token
        if is_oauth_token:
            orders_result = get_orders_for_item(user_token, item_id)
            if orders_result['success'] and orders_result['orders']:
                # Use the first order found
                order_data = orders_result['orders'][0]
                order_details = get_order_with_tax_breakdown(user_token, order_data)
                if order_details['success']:
                    
                    # Get transaction data
                    transaction_data = order_details['transaction_data']
                    
                    # Try to get additional fee information
                    fee_details = get_ebay_fees_from_order_api(order_data['orderId'])
                    if fee_details['success']:
                        # Merge fee data with transaction data
                        transaction_data.update(fee_details['fee_data'])
                    else:
                        pass  # Fee details failed, continue with basic transaction data
                    
                    return {
                        'success': True,
                        'transaction_data': transaction_data
                    }
                else:
                    pass  # Order details failed
            else:
                pass  # No orders found
        else:
            pass  # Skipping modern Order API
        
        # Fallback: try legacy approach
        
        # First try to get basic item info and price
        basic_price = get_basic_item_price(user_token, item_id)
        
        if basic_price > 0:
            # Try to get transaction identifiers
            transaction_info = get_transaction_identifiers(user_token, item_id)
            if transaction_info['success']:
                
                # Try each transaction ID
                transaction_data = {
                    'final_price': basic_price,
                    'listing_fees': 0,
                    'final_value_fee': 0,
                    'paypal_fee': 0,
                    'sales_tax': 0,
                    'net_earnings': 0,
                    'total_fees': 0,
                    'has_actual_fees': False
                }
                
                for transaction_id, transaction_type in transaction_info['transactions']:
                    detailed_data = get_specific_transaction_details(user_token, transaction_id, transaction_type)
                    if detailed_data['success'] and detailed_data['transaction_data']['final_price'] > 0:
                        transaction_data = detailed_data['transaction_data']
                        break
                
                # If no transaction data found, try order IDs
                if transaction_data['final_price'] == basic_price and transaction_data['final_value_fee'] == 0:
                    for order_id in transaction_info['orders']:
                        order_data = get_order_details_by_id(user_token, order_id)
                        if order_data['success'] and order_data['transaction_data']['final_price'] > 0:
                            transaction_data = order_data['transaction_data']
                            break
                
                # If we found actual fees, use them
                if transaction_data['final_value_fee'] > 0 or transaction_data['sales_tax'] > 0:
                    transaction_data['has_actual_fees'] = True
                else:
                    # Calculate proper fee estimates
                    if basic_price > 0:
                        # eBay Final Value Fee: 10% for most categories (up to $750), then 2% above $750
                        if basic_price <= 750:
                            transaction_data['final_value_fee'] = basic_price * 0.10
                        else:
                            transaction_data['final_value_fee'] = (750 * 0.10) + ((basic_price - 750) * 0.02)
                        
                        # PayPal fee: 2.9% + $0.30
                        transaction_data['paypal_fee'] = (basic_price * 0.029) + 0.30
                        
                        # Listing fee
                        transaction_data['listing_fees'] = 0.35
                        
                        # Total fees
                        transaction_data['total_fees'] = transaction_data['final_value_fee'] + transaction_data['paypal_fee'] + transaction_data['listing_fees']
                        
                        # Net earnings
                        transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['total_fees']
                        
            else:
                pass  # Fee calculation failed, continue with basic data
        else:
            pass  # Transaction data not available
        
        # If still no data, use estimates
        if transaction_data['final_price'] == 0:
            # Get basic price from selling status
            basic_price = get_basic_item_price(user_token, item_id)
            if basic_price > 0:
                transaction_data['final_price'] = basic_price
                transaction_data['subtotal'] = basic_price  # Assume subtotal equals final price if not available
                transaction_data['shipping'] = 0  # Assume free shipping if not available
                
                # eBay Final Value Fee: 10% for most categories (up to $750), then 2% above $750
                if basic_price <= 750:
                    transaction_data['final_value_fee'] = basic_price * 0.10
                else:
                    transaction_data['final_value_fee'] = (750 * 0.10) + ((basic_price - 750) * 0.02)
                
                # PayPal fee: 2.9% + $0.30 (if using PayPal)
                transaction_data['paypal_fee'] = (basic_price * 0.029) + 0.30
                
                # eBay listing fee: Usually $0.35 for basic listings
                transaction_data['listing_fees'] = 0.35
                
                # Sales tax: Usually not charged by seller (buyer pays)
                transaction_data['sales_tax'] = 0
                
                # Total fees calculation
                transaction_data['total_fees'] = transaction_data['final_value_fee'] + transaction_data['paypal_fee'] + transaction_data['listing_fees']
                
                # Net earnings = final price - total fees
                transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['total_fees']
                
                print(f"  Final Value Fee (10%): ${transaction_data['final_value_fee']:.2f}")
                print(f"  PayPal Fee: ${transaction_data['paypal_fee']:.2f}")
                print(f"  Listing Fee: ${transaction_data['listing_fees']:.2f}")
                print(f"  Total Fees: ${transaction_data['total_fees']:.2f}")
                print(f"  Net Earnings: ${transaction_data['net_earnings']:.2f}")
        
        return {
            'success': True,
            'transaction_data': transaction_data
        }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Order API error: {}'.format(str(e))
        }

def get_orders_for_item(user_token, item_id):
    """
    Get orders for a specific item using Trading API GetOrders call
    """
    try:
        import xml.etree.ElementTree as ET
        from datetime import datetime, timedelta
        
        url = "https://api.ebay.com/ws/api.dll"
        
        # Calculate date range - last 30 days (eBay recommendation)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Format dates for eBay API
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        
        xml_request = f"""<?xml version="1.0" encoding="utf-8"?>
        <GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{user_token}</eBayAuthToken>
            </RequesterCredentials>
            <CreateTimeFrom>{start_date_str}</CreateTimeFrom>
            <CreateTimeTo>{end_date_str}</CreateTimeTo>
            <DetailLevel>ReturnAll</DetailLevel>
            <IncludeFinalValueFee>true</IncludeFinalValueFee>
            <Version>1193</Version>
        </GetOrdersRequest>"""
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1193',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetOrders',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': f'eBay API error: {error_msg.text}'
                    }
            
            # Iterate through orders and transactions
            matching_orders = []
            orders = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Order')
            
            print(f"DEBUG: Found {len(orders)} orders in date range")
            
            for order in orders:
                order_id = order.find('.//{urn:ebay:apis:eBLBaseComponents}OrderID')
                transactions = order.findall('.//{urn:ebay:apis:eBLBaseComponents}Transaction')
                
                print(f"DEBUG: Order {order_id.text if order_id is not None else 'Unknown'} has {len(transactions)} transactions")
                
                # Iterate through transactions in this order
                for transaction in transactions:
                    item_elem = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}Item')
                    if item_elem is not None:
                        item_id_elem = item_elem.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                        if item_id_elem is not None and item_id_elem.text == item_id:
                            print(f"DEBUG: Found matching item {item_id} in order {order_id.text}")
                            matching_orders.append({
                                'orderId': order_id.text if order_id is not None else 'Unknown',
                                'transaction': transaction,
                                'order': order
                            })
                            break
            
            print(f"DEBUG: Found {len(matching_orders)} matching orders")
            return {
                'success': True,
                'orders': matching_orders
            }
        else:
            print("DEBUG: GetOrders failed with status {}".format(response.status_code))
            return {
                'success': False,
                'error': f'GetOrders failed: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        print("DEBUG: GetOrders exception: {}".format(str(e)))
        return {
            'success': False,
            'error': f'GetOrders error: {str(e)}'
        }

def get_order_with_tax_breakdown(user_token, order_data):
    """
    Extract detailed order information from Trading API GetOrders response
    """
    try:
        import xml.etree.ElementTree as ET
        
        order = order_data['order']
        transaction = order_data['transaction']
        
        print(f"DEBUG: Processing order {order_data['orderId']}")
        
        # Debug: Print all XML elements to see what's available
        print("DEBUG: Available order elements:")
        for elem in order.iter():
            if elem.text and elem.text.strip():
                print(f"  {elem.tag.split('}')[-1]}: {elem.text}")
        
        print("DEBUG: Available transaction elements:")
        for elem in transaction.iter():
            if elem.text and elem.text.strip():
                print(f"  {elem.tag.split('}')[-1]}: {elem.text}")
        
        transaction_data = {
            'final_price': 0,
            'subtotal': 0,
            'shipping': 0,
            'listing_fees': 0,
            'final_value_fee': 0,
            'paypal_fee': 0,
            'sales_tax': 0,
            'net_earnings': 0,
            'total_fees': 0,
            'has_actual_fees': True,
            'order_id': order_data['orderId']
        }
        
        # Extract transaction price
        transaction_price = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}TransactionPrice')
        if transaction_price is not None:
            transaction_data['final_price'] = float(transaction_price.text) if transaction_price.text else 0
        
        # Extract subtotal
        subtotal = order.find('.//{urn:ebay:apis:eBLBaseComponents}Subtotal')
        if subtotal is not None:
            transaction_data['subtotal'] = float(subtotal.text) if subtotal.text else 0
        
        # Extract shipping cost - try multiple possible element names
        shipping_cost = order.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingCost')
        if shipping_cost is not None:
            transaction_data['shipping'] = float(shipping_cost.text) if shipping_cost.text else 0
            print(f"DEBUG: Found shipping cost from ShippingCost: {transaction_data['shipping']}")
        else:
            # Try alternative shipping element names
            shipping_service_cost = order.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingServiceCost')
            if shipping_service_cost is not None:
                transaction_data['shipping'] = float(shipping_service_cost.text) if shipping_service_cost.text else 0
                print(f"DEBUG: Found shipping cost from ShippingServiceCost: {transaction_data['shipping']}")
            else:
                # Try in transaction element
                transaction_shipping = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingCost')
                if transaction_shipping is not None:
                    transaction_data['shipping'] = float(transaction_shipping.text) if transaction_shipping.text else 0
                    print(f"DEBUG: Found shipping cost from transaction ShippingCost: {transaction_data['shipping']}")
                else:
                    transaction_shipping_service = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}ShippingServiceCost')
                    if transaction_shipping_service is not None:
                        transaction_data['shipping'] = float(transaction_shipping_service.text) if transaction_shipping_service.text else 0
                        print(f"DEBUG: Found shipping cost from transaction ShippingServiceCost: {transaction_data['shipping']}")
                    else:
                        # Try ActualShippingCost element
                        actual_shipping_cost = order.find('.//{urn:ebay:apis:eBLBaseComponents}ActualShippingCost')
                        if actual_shipping_cost is not None:
                            transaction_data['shipping'] = float(actual_shipping_cost.text) if actual_shipping_cost.text else 0
                            print(f"DEBUG: Found shipping cost from ActualShippingCost: {transaction_data['shipping']}")
                        else:
                            transaction_data['shipping'] = 0
                            print(f"DEBUG: No shipping cost found in order/transaction XML")
        
        # Extract order total (might be different from transaction price)
        order_total = order.find('.//{urn:ebay:apis:eBLBaseComponents}Total')
        if order_total is not None:
            transaction_data['final_price'] = float(order_total.text) if order_total.text else transaction_data['final_price']
        
        # Extract Final Value Fee
        fvf = order.find('.//{urn:ebay:apis:eBLBaseComponents}FinalValueFee')
        if fvf is not None:
            transaction_data['final_value_fee'] = float(fvf.text) if fvf.text else 0
        
        # Extract sales tax
        sales_tax = order.find('.//{urn:ebay:apis:eBLBaseComponents}SalesTax')
        if sales_tax is not None:
            transaction_data['sales_tax'] = float(sales_tax.text) if sales_tax.text else 0
        
        # Extract fees from Fees section
        fees_section = order.find('.//{urn:ebay:apis:eBLBaseComponents}Fees')
        if fees_section is not None:
            fees = fees_section.findall('.//{urn:ebay:apis:eBLBaseComponents}Fee')
            for fee in fees:
                fee_name = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Name')
                fee_amount = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Fee')
                
                if fee_name is not None and fee_amount is not None:
                    fee_name_text = fee_name.text.lower() if fee_name.text else ''
                    fee_amount_val = float(fee_amount.text) if fee_amount.text else 0
                    
                    if 'final value' in fee_name_text:
                        transaction_data['final_value_fee'] += fee_amount_val
                    elif 'paypal' in fee_name_text:
                        transaction_data['paypal_fee'] += fee_amount_val
                    elif 'listing' in fee_name_text or 'insertion' in fee_name_text:
                        transaction_data['listing_fees'] += fee_amount_val
        
        # Calculate total fees
        transaction_data['total_fees'] = (
            transaction_data['final_value_fee'] + 
            transaction_data['paypal_fee'] + 
            transaction_data['listing_fees']
        )
        
        # Calculate net earnings
        transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['total_fees']
        
        print(f"DEBUG: Extracted order data:")
        print(f"  Final Price: ${transaction_data['final_price']:.2f}")
        print(f"  Subtotal: ${transaction_data['subtotal']:.2f}")
        print(f"  Shipping: ${transaction_data['shipping']:.2f}")
        print(f"  Final Value Fee: ${transaction_data['final_value_fee']:.2f}")
        print(f"  PayPal Fee: ${transaction_data['paypal_fee']:.2f}")
        print(f"  Listing Fees: ${transaction_data['listing_fees']:.2f}")
        print(f"  Sales Tax: ${transaction_data['sales_tax']:.2f}")
        print(f"  Total Fees: ${transaction_data['total_fees']:.2f}")
        print(f"  Net Earnings: ${transaction_data['net_earnings']:.2f}")
        
        return {
            'success': True,
            'transaction_data': transaction_data
        }
        
    except Exception as e:
        print(f"DEBUG: Error processing order data: {str(e)}")
        return {
            'success': False,
            'error': f'Order processing error: {str(e)}'
        }
        
        if response.status_code == 200:
            data = response.json()
            
            print("DEBUG: Order data keys: {}".format(list(data.keys())))
            
            # Extract financial details from modern Order API response
            transaction_data = {
                'final_price': 0,
                'subtotal': 0,
                'shipping': 0,
                'listing_fees': 0,
                'final_value_fee': 0,
                'paypal_fee': 0,
                'sales_tax': 0,
                'net_earnings': 0,
                'total_fees': 0,
                'has_actual_fees': True  # Modern API provides actual data
            }
            
            # Get order total
            pricing_summary = data.get('pricingSummary', {})
            if pricing_summary:
                transaction_data['final_price'] = float(pricing_summary.get('total', 0))
                print("DEBUG: Pricing summary: {}".format(pricing_summary))
            
            # Get tax breakdown
            tax_details = data.get('taxDetails', [])
            print("DEBUG: Tax details: {}".format(tax_details))
            for tax in tax_details:
                tax_type = tax.get('taxType', '').lower()
                tax_amount = float(tax.get('amount', {}).get('value', 0))
                
                if 'sales' in tax_type or 'vat' in tax_type:
                    transaction_data['sales_tax'] += tax_amount
                elif 'shipping' in tax_type:
                    # Shipping tax is separate from sales tax
                    pass
            
            # Get fee breakdown
            fee_details = data.get('feeDetails', [])
            print("DEBUG: Fee details: {}".format(fee_details))
            for fee in fee_details:
                fee_type = fee.get('feeType', '').lower()
                fee_amount = float(fee.get('amount', {}).get('value', 0))
                
                if 'final value' in fee_type or 'transaction' in fee_type:
                    transaction_data['final_value_fee'] += fee_amount
                elif 'listing' in fee_type:
                    transaction_data['listing_fees'] += fee_amount
                elif 'paypal' in fee_type or 'payment' in fee_type:
                    transaction_data['paypal_fee'] += fee_amount
            
            # Calculate totals
            transaction_data['total_fees'] = transaction_data['listing_fees'] + transaction_data['final_value_fee'] + transaction_data['paypal_fee']
            transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['sales_tax'] - transaction_data['final_value_fee']
            
            print("DEBUG: Calculated transaction data: {}".format(transaction_data))
            
            return {
                'success': True,
                'transaction_data': transaction_data
            }
        else:
            print("DEBUG: Order details API failed with status {}".format(response.status_code))
            return {
                'success': False,
                'error': 'Order API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        print("DEBUG: Order details API exception: {}".format(str(e)))
        return {
            'success': False,
            'error': 'Order API error: {}'.format(str(e))
        }

def get_transaction_identifiers(user_token, item_id):
    """
    Get transaction IDs and order IDs from GetMyeBaySelling for a specific item
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = "https://api.ebay.com/ws/api.dll"
        
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <SoldList>
                <Include>true</Include>
                <Pagination>
                    <EntriesPerPage>100</EntriesPerPage>
                    <PageNumber>1</PageNumber>
                </Pagination>
            </SoldList>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetMyeBaySellingRequest>""".format(user_token)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': 'eBay API error: {}'.format(error_msg.text)
                    }
            
            # Find the specific item and extract transaction/order IDs
            transactions = []
            orders = []
            
            sold_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}SoldList')
            if sold_list is not None:
                items = sold_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                for item in items:
                    item_id_elem = item.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                    if item_id_elem is not None and item_id_elem.text == item_id:
                        # Found the item, now get transaction/order IDs
                        item_transactions = item.findall('.//{urn:ebay:apis:eBLBaseComponents}Transaction')
                        for trans in item_transactions:
                            trans_id = trans.find('.//{urn:ebay:apis:eBLBaseComponents}TransactionID')
                            trans_type = trans.find('.//{urn:ebay:apis:eBLBaseComponents}TransactionType')
                            order_id = trans.find('.//{urn:ebay:apis:eBLBaseComponents}OrderID')
                            
                            if trans_id is not None and trans_type is not None:
                                transactions.append((trans_id.text, trans_type.text))
                            if order_id is not None:
                                orders.append(order_id.text)
                        break
            
            return {
                'success': True,
                'transactions': transactions,
                'orders': orders
            }
        else:
            return {
                'success': False,
                'error': 'API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'API error: {}'.format(str(e))
        }

# eBay Fee Retrieval Functions
def get_ebay_fees_from_order_api(order_id):
    """
    Retrieve fee information using Order API
    """
    try:
        token_result = get_valid_ebay_token()
        if not token_result['success']:
            return token_result
        
        api_base_url = app.config.get('EBAY_API_BASE_URL', 'https://api.ebay.com')
        url = f"{api_base_url}/sell/fulfillment/v1/order/{order_id}"
        
        headers = {
            'Authorization': f"Bearer {token_result['access_token']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        # Request fee breakdown specifically
        params = {
            'fieldGroups': 'TAX_BREAKDOWN,FEE_BREAKDOWN'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return extract_fee_data(data)
        else:
            return {'success': False, 'error': f'Order API failed: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_fee_data(order_data):
    """
    Extract fee information from Order API response
    """
    try:
        print("DEBUG: Extracting fee data from order response")
        print(f"DEBUG: Order data keys: {list(order_data.keys())}")
        
        fee_data = {}
        
        # Extract from lineItems
        line_items = order_data.get('lineItems', [])
        print(f"DEBUG: Found {len(line_items)} line items")
        total_fees = 0
        
        for i, item in enumerate(line_items):
            print(f"DEBUG: Line item {i}: {list(item.keys())}")
            
            # Final Value Fee
            fvf = item.get('finalValueFee', {})
            if fvf:
                fee_data['final_value_fee'] = float(fvf.get('value', 0))
                total_fees += fee_data['final_value_fee']
                print(f"DEBUG: Final Value Fee: {fee_data['final_value_fee']}")
            
            # Insertion Fee
            insertion_fee = item.get('insertionFee', {})
            if insertion_fee:
                fee_data['insertion_fee'] = float(insertion_fee.get('value', 0))
                total_fees += fee_data['insertion_fee']
                print(f"DEBUG: Insertion Fee: {fee_data['insertion_fee']}")
        
        # Extract from pricingSummary
        pricing = order_data.get('pricingSummary', {})
        if pricing:
            fee_data['total_fees'] = total_fees
            fee_data['net_amount'] = float(pricing.get('total', 0)) - total_fees
            print(f"DEBUG: Total fees: {total_fees}, Net amount: {fee_data['net_amount']}")
        
        print(f"DEBUG: Final fee data: {fee_data}")
        return {
            'success': True,
            'fee_data': fee_data
        }
        
    except Exception as e:
        print(f"DEBUG: Fee extraction error: {str(e)}")
        return {'success': False, 'error': f'Fee extraction error: {str(e)}'}

def get_ebay_final_value_fees_trading_api(order_ids):
    """
    Retrieve Final Value Fees using Trading API GetOrders (Most Reliable)
    """
    try:
        token_result = get_valid_ebay_token()
        if not token_result['success']:
            return token_result
        
        url = "https://api.ebay.com/ws/api.dll"
        
        headers = {
            'X-EBAY-API-CALL-NAME': 'GetOrders',
            'X-EBAY-API-VERSION': '1193',
            'X-EBAY-API-SITEID': '0',
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1193',
            'Content-Type': 'text/xml'
        }
        
        # Build XML request with order IDs
        order_xml = ''.join([f'<OrderID>{order_id}</OrderID>' for order_id in order_ids])
        
        xml_body = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{token_result['access_token']}</eBayAuthToken>
            </RequesterCredentials>
            <OrderIDArray>
                {order_xml}
            </OrderIDArray>
            <IncludeFinalValueFee>true</IncludeFinalValueFee>
            <DetailLevel>ReturnAll</DetailLevel>
        </GetOrdersRequest>
        """
        
        response = requests.post(url, headers=headers, data=xml_body)
        
        if response.status_code == 200:
            return parse_fvf_from_xml(response.text)
        else:
            return {'success': False, 'error': f'GetOrders failed: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def parse_fvf_from_xml(xml_response):
    """
    Parse Final Value Fee data from Trading API XML response
    """
    try:
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(xml_response)
        
        # Check for errors
        errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
        if errors:
            error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
            if error_msg is not None:
                return {'success': False, 'error': f'eBay API error: {error_msg.text}'}
        
        # Extract FVF data
        fvf_data = []
        orders = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Order')
        
        for order in orders:
            order_id = order.find('.//{urn:ebay:apis:eBLBaseComponents}OrderID')
            fvf = order.find('.//{urn:ebay:apis:eBLBaseComponents}FinalValueFee')
            
            if order_id is not None and fvf is not None:
                fvf_data.append({
                    'order_id': order_id.text,
                    'final_value_fee': float(fvf.text) if fvf.text else 0.0
                })
        
        return {
            'success': True,
            'fvf_data': fvf_data
        }
        
    except Exception as e:
        return {'success': False, 'error': f'XML parsing error: {str(e)}'}

def get_specific_transaction_details(user_token, transaction_id, transaction_type):
    """
    Get specific transaction details using transaction ID and type
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = "https://api.ebay.com/ws/api.dll"
        
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetItemTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <TransactionID>{}</TransactionID>
            <TransactionType>{}</TransactionType>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetItemTransactionsRequest>""".format(user_token, transaction_id, transaction_type)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetItemTransactions',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': 'Transaction API error: {}'.format(error_msg.text)
                    }
            
            # Extract transaction financial details
            transaction_data = {
                'final_price': 0,
                'subtotal': 0,
                'shipping': 0,
                'listing_fees': 0,
                'final_value_fee': 0,
                'paypal_fee': 0,
                'sales_tax': 0,
                'net_earnings': 0,
                'total_fees': 0,
                'has_actual_fees': False
            }
            
            # Parse transaction details
            transactions = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Transaction')
            if transactions:
                transaction = transactions[0]
                
                # Get transaction price
                transaction_price = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}TransactionPrice')
                if transaction_price is not None:
                    transaction_data['final_price'] = float(transaction_price.text) if transaction_price.text else 0
                
                # Get fees from transaction
                fees = transaction.find('.//{urn:ebay:apis:eBLBaseComponents}Fees')
                if fees is not None:
                    fee_list = fees.findall('.//{urn:ebay:apis:eBLBaseComponents}Fee')
                    for fee in fee_list:
                        fee_name = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Name')
                        fee_amount = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Fee')
                        if fee_name is not None and fee_amount is not None:
                            fee_name_text = fee_name.text.lower() if fee_name.text else ''
                            fee_amount_val = float(fee_amount.text) if fee_amount.text else 0
                            
                            if 'listing' in fee_name_text:
                                transaction_data['listing_fees'] += fee_amount_val
                            elif 'final value' in fee_name_text or 'transaction' in fee_name_text:
                                transaction_data['final_value_fee'] += fee_amount_val
                            elif 'paypal' in fee_name_text:
                                transaction_data['paypal_fee'] += fee_amount_val
                            elif 'tax' in fee_name_text:
                                transaction_data['sales_tax'] += fee_amount_val
                    
                    # Mark that we found actual fees
                    if transaction_data['final_value_fee'] > 0 or transaction_data['sales_tax'] > 0:
                        transaction_data['has_actual_fees'] = True
                
                # Calculate net earnings
                transaction_data['total_fees'] = transaction_data['listing_fees'] + transaction_data['final_value_fee'] + transaction_data['paypal_fee']
                transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['sales_tax'] - transaction_data['final_value_fee']
            
            return {
                'success': True,
                'transaction_data': transaction_data
            }
        else:
            return {
                'success': False,
                'error': 'Transaction API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Transaction API error: {}'.format(str(e))
        }

def get_order_details_by_id(user_token, order_id):
    """
    Get order details using order ID (for sales orders)
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = "https://api.ebay.com/ws/api.dll"
        
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <OrderIDArray>
                <OrderID>{}</OrderID>
            </OrderIDArray>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetOrdersRequest>""".format(user_token, order_id)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetOrders',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': 'Order API error: {}'.format(error_msg.text)
                    }
            
            # Extract order financial details
            transaction_data = {
                'final_price': 0,
                'subtotal': 0,
                'shipping': 0,
                'listing_fees': 0,
                'final_value_fee': 0,
                'paypal_fee': 0,
                'sales_tax': 0,
                'net_earnings': 0,
                'total_fees': 0,
                'has_actual_fees': False
            }
            
            # Parse order details
            orders = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Order')
            if orders:
                order = orders[0]
                
                # Get order total
                total = order.find('.//{urn:ebay:apis:eBLBaseComponents}Total')
                if total is not None:
                    transaction_data['final_price'] = float(total.text) if total.text else 0
                
                # Get sales tax
                sales_tax = order.find('.//{urn:ebay:apis:eBLBaseComponents}SalesTax')
                if sales_tax is not None:
                    transaction_data['sales_tax'] = float(sales_tax.text) if sales_tax.text else 0
                
                # Get fees
                fees = order.find('.//{urn:ebay:apis:eBLBaseComponents}Fees')
                if fees is not None:
                    fee_list = fees.findall('.//{urn:ebay:apis:eBLBaseComponents}Fee')
                    for fee in fee_list:
                        fee_name = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Name')
                        fee_amount = fee.find('.//{urn:ebay:apis:eBLBaseComponents}Fee')
                        if fee_name is not None and fee_amount is not None:
                            fee_name_text = fee_name.text.lower() if fee_name.text else ''
                            fee_amount_val = float(fee_amount.text) if fee_amount.text else 0
                            
                            if 'final value' in fee_name_text:
                                transaction_data['final_value_fee'] += fee_amount_val
                            elif 'paypal' in fee_name_text:
                                transaction_data['paypal_fee'] += fee_amount_val
                    
                    # Mark that we found actual fees
                    if transaction_data['final_value_fee'] > 0 or transaction_data['sales_tax'] > 0:
                        transaction_data['has_actual_fees'] = True
                
                # Calculate net earnings
                transaction_data['total_fees'] = transaction_data['listing_fees'] + transaction_data['final_value_fee'] + transaction_data['paypal_fee']
                transaction_data['net_earnings'] = transaction_data['final_price'] - transaction_data['sales_tax'] - transaction_data['final_value_fee']
            
            return {
                'success': True,
                'transaction_data': transaction_data
            }
        else:
            return {
                'success': False,
                'error': 'Order API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Order API error: {}'.format(str(e))
        }

def get_basic_item_price(user_token, item_id):
    """
    Get basic item price from GetMyeBaySelling as fallback
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = "https://api.ebay.com/ws/api.dll"
        
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <SoldList>
                <Include>true</Include>
                <Pagination>
                    <EntriesPerPage>100</EntriesPerPage>
                    <PageNumber>1</PageNumber>
                </Pagination>
            </SoldList>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetMyeBaySellingRequest>""".format(user_token)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
            'X-EBAY-API-SITEID': '0',
            'Content-Type': 'text/xml'
        }
        
        print("DEBUG: Calling GetMyeBaySelling for item: {}".format(item_id))
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        print("DEBUG: GetMyeBaySelling response status: {}".format(response.status_code))
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    print("DEBUG: GetMyeBaySelling error: {}".format(error_msg.text))
                    return 0
            
            # Find the specific item and get its price
            sold_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}SoldList')
            if sold_list is not None:
                items = sold_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                print("DEBUG: Found {} sold items in GetMyeBaySelling".format(len(items)))
                
                for item in items:
                    item_id_elem = item.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                    if item_id_elem is not None and item_id_elem.text == item_id:
                        print("DEBUG: Found matching item in sold list")
                        selling_status = item.find('.//{urn:ebay:apis:eBLBaseComponents}SellingStatus')
                        if selling_status is not None:
                            current_price = selling_status.find('.//{urn:ebay:apis:eBLBaseComponents}CurrentPrice')
                            if current_price is not None:
                                price = float(current_price.text) if current_price.text else 0
                                print("DEBUG: Found item price: {}".format(price))
                                return price
                        break
                else:
                    print("DEBUG: Item not found in sold list")
            else:
                print("DEBUG: No sold list found in response")
            
            return 0
        else:
            print("DEBUG: GetMyeBaySelling failed with status: {}".format(response.status_code))
            return 0
            
    except Exception as e:
        print("DEBUG: GetMyeBaySelling exception: {}".format(str(e)))
        return 0


def get_ebay_recently_sold_items(user_token, api_base_url):
    """
    Get recently sold items from eBay using Browse API (works with your current token)
    This searches for completed/sold items from the last 2 weeks
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate date 2 weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        date_filter = two_weeks_ago.strftime('%Y-%m-%d')
        
        # Browse API endpoint for completed items
        url = "{}/buy/browse/v1/item_summary/search".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(user_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        # Search parameters for recently sold items
        max_listings = app.config.get('EBAY_MAX_LISTINGS', 200)
        params = {
            'q': 'pokemon cards',  # More specific search term
            'limit': min(max_listings, 200),  # Maximum allowed by Browse API is 200
            'offset': 0,
            'filter': 'deliveryCountry:US,conditionIds:{1000|1500|2000|2500|3000|4000|5000}',  # Various conditions
            'sort': 'endTime:desc'  # Sort by end time descending (most recent first)
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            item_summaries = data.get('itemSummaries', [])
            
            # Process the results to match our expected format
            listings = []
            for item in item_summaries:
                # Extract relevant information
                item_id = item.get('itemId', 'N/A')
                title = item.get('title', 'N/A')
                price_info = item.get('price', {})
                price = price_info.get('value', 0) if price_info else 0
                currency = price_info.get('currency', 'USD') if price_info else 'USD'
                condition = item.get('condition', 'N/A')
                image_url = item.get('image', {}).get('imageUrl') if item.get('image') else None
                seller = item.get('seller', {}).get('username', 'Unknown')
                
                # Get end time (when the item ended/sold)
                end_time = item.get('itemEndDate', 'N/A')
                
                # Check if item has ended (completed/sold)
                item_web_url = item.get('itemWebUrl', '')
                is_completed = 'ended' in item_web_url.lower() or end_time != 'N/A'
                
                listings.append({
                    'itemId': item_id,
                    'title': title,
                    'description': title,  # Use title as description since Browse API doesn't provide separate description
                    'price': float(price) if price else 0,
                    'currency': currency,
                    'condition': condition,
                    'image_url': image_url,
                    'seller': seller,
                    'sku': item_id,  # Use itemId as SKU for consistency
                    'ebay_url': 'https://www.ebay.com/itm/{}'.format(item_id),
                    'category': item.get('categories', [{}])[0].get('categoryName', 'N/A') if item.get('categories') else 'N/A',
                    'quantity': 1,  # Browse API doesn't provide quantity info
                    'end_time': end_time,
                    'status': 'Sold' if is_completed else 'Active'  # Mark as sold if completed
                })
            
            return {
                'success': True,
                'listings': listings,
                'total': len(listings),
                'note': 'Using Browse API - showing eBay items (mix of active and recently sold)'
            }
        else:
            return {
                'success': False,
                'error': 'Browse API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Browse API error: {}'.format(str(e))
        }

def get_ebay_listings_via_browse(user_token, api_base_url):
    """
    Get listings using Browse API (works with your current token)
    This searches for items by seller, but requires knowing your eBay username
    """
    try:
        # Browse API endpoint
        url = "{}/buy/browse/v1/item_summary/search".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(user_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        # Search parameters - you'll need to replace 'your_ebay_username' with your actual eBay username
        max_listings = app.config.get('EBAY_MAX_LISTINGS', 200)
        params = {
            'q': '*',  # Search all items
            'limit': min(max_listings, 200),  # Maximum allowed by Browse API is 200
            'offset': 0,
            'filter': 'deliveryCountry:US,deliveryPostalCode:US'  # Limit to US
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            item_summaries = data.get('itemSummaries', [])
            
            # Process the results to match our expected format
            listings = []
            for item in item_summaries:
                # Extract relevant information
                item_id = item.get('itemId', 'N/A')
                title = item.get('title', 'N/A')
                price_info = item.get('price', {})
                price = price_info.get('value', 0) if price_info else 0
                currency = price_info.get('currency', 'USD') if price_info else 'USD'
                condition = item.get('condition', 'N/A')
                image_url = item.get('image', {}).get('imageUrl') if item.get('image') else None
                seller = item.get('seller', {}).get('username', 'Unknown')
                
                listings.append({
                    'itemId': item_id,
                    'title': title,
                    'description': title,  # Use title as description since Browse API doesn't provide separate description
                    'price': float(price) if price else 0,
                    'currency': currency,
                    'condition': condition,
                    'image_url': image_url,
                    'seller': seller,
                    'sku': item_id,  # Use itemId as SKU for consistency
                    'ebay_url': 'https://www.ebay.com/itm/{}'.format(item_id),
                    'category': item.get('categories', [{}])[0].get('categoryName', 'N/A') if item.get('categories') else 'N/A',
                    'quantity': 1  # Browse API doesn't provide quantity info
                })
            
            return {
                'success': True,
                'listings': listings,
                'total': len(listings),
                'note': 'Using Browse API - showing sample eBay listings (not filtered by seller)'
            }
        else:
            return {
                'success': False,
                'error': 'Browse API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Browse API error: {}'.format(str(e))
        }

def get_ebay_listings_legacy(user_token):
    """
    Fetch listings using legacy eBay Trading API
    """
    try:
        import xml.etree.ElementTree as ET
        
        # eBay Trading API endpoint
        url = "https://api.ebay.com/ws/api.dll"
        
        # XML request for GetMyeBaySelling
        xml_request = """<?xml version="1.0" encoding="utf-8"?>
        <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>{}</eBayAuthToken>
            </RequesterCredentials>
            <ActiveList>
                <Include>true</Include>
                <Pagination>
                    <EntriesPerPage>100</EntriesPerPage>
                    <PageNumber>1</PageNumber>
                </Pagination>
            </ActiveList>
            <DetailLevel>ReturnAll</DetailLevel>
            <Version>1199</Version>
        </GetMyeBaySellingRequest>""".format(user_token)
        
        headers = {
            'X-EBAY-API-COMPATIBILITY-LEVEL': '1199',
            'X-EBAY-API-DEV-NAME': app.config.get('EBAY_DEV_NAME', 'your_dev_name'),
            'X-EBAY-API-APP-NAME': app.config.get('EBAY_APP_NAME', 'your_app_name'),
            'X-EBAY-API-CERT-NAME': app.config.get('EBAY_CERT_NAME', 'your_cert_name'),
            'X-EBAY-API-CALL-NAME': 'GetMyeBaySelling',
            'X-EBAY-API-SITEID': '0',  # US site
            'Content-Type': 'text/xml'
        }
        
        response = requests.post(url, data=xml_request, headers=headers)
        
        if response.status_code == 200:
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//{urn:ebay:apis:eBLBaseComponents}Errors')
            if errors:
                error_msg = errors[0].find('.//{urn:ebay:apis:eBLBaseComponents}LongMessage')
                if error_msg is not None:
                    return {
                        'success': False,
                        'error': 'eBay API error: {}'.format(error_msg.text)
                    }
            
            # Extract listings
            listings = []
            active_list = root.find('.//{urn:ebay:apis:eBLBaseComponents}ActiveList')
            if active_list is not None:
                items = active_list.findall('.//{urn:ebay:apis:eBLBaseComponents}Item')
                for item in items:
                    item_id = item.find('.//{urn:ebay:apis:eBLBaseComponents}ItemID')
                    title = item.find('.//{urn:ebay:apis:eBLBaseComponents}Title')
                    current_price = item.find('.//{urn:ebay:apis:eBLBaseComponents}CurrentPrice')
                    condition = item.find('.//{urn:ebay:apis:eBLBaseComponents}ConditionDisplayName')
                    quantity = item.find('.//{urn:ebay:apis:eBLBaseComponents}Quantity')
                    
                    listings.append({
                        'itemId': item_id.text if item_id is not None else 'N/A',
                        'title': title.text if title is not None else 'N/A',
                        'price': float(current_price.text) if current_price is not None and current_price.text else 0,
                        'condition': condition.text if condition is not None else 'N/A',
                        'quantity': int(quantity.text) if quantity is not None and quantity.text else 0,
                        'sku': item_id.text if item_id is not None else 'N/A'
                    })
            
            return {
                'success': True,
                'listings': listings,
                'total': len(listings),
                'note': 'Using legacy Trading API'
            }
        else:
            return {
                'success': False,
                'error': 'Legacy API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Legacy API error: {}'.format(str(e))
        }

def get_ebay_listings_modern(user_token, api_base_url):
    """
    Fetch listings using modern eBay APIs (OAuth 2.0)
    """
    try:
        # Try Inventory API first
        url = "{}/sell/inventory/v1/inventory_item".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(user_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        params = {
            'limit': 200,  # Maximum allowed by eBay APIs
            'offset': 0
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listings': data.get('inventoryItems', []),
                'total': data.get('total', 0),
                'note': 'Using modern Inventory API'
            }
        elif response.status_code == 403:
            # Try Browse API as fallback
            return try_alternative_ebay_endpoints(user_token, api_base_url)
        else:
            return {
                'success': False,
                'error': 'Modern API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Modern API error: {}'.format(str(e))
        }

def try_alternative_ebay_endpoints(user_token, api_base_url):
    """
    Try alternative eBay API endpoints when the main one fails
    """
    try:
        # Try Browse API to search for items
        url = "{}/buy/browse/v1/item_summary/search".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(user_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        # Search parameters - you might need to adjust these
        params = {
            'q': '*',  # Search for all items
            'limit': 200,  # Maximum allowed by Browse API
            'offset': 0,
            'filter': 'conditionIds:{1000|1500|2000|2500|3000|4000|5000}'  # Various conditions
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listings': data.get('itemSummaries', []),
                'total': data.get('total', 0),
                'note': 'Using Browse API - may show all items, not just yours'
            }
        else:
            return {
                'success': False,
                'error': 'eBay API access denied. Please check: 1) Your token has the correct permissions (selling.read, selling.write), 2) Your token is not expired, 3) You are using the correct token format. Error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Alternative API error: {}'.format(str(e))
        }

def get_ebay_listings_oauth(access_token, api_base_url):
    """
    Fetch listings using OAuth 2.0 access token
    """
    try:
        # Try Inventory API first (most comprehensive for seller data)
        url = "{}/sell/inventory/v1/inventory_item".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        params = {
            'limit': 200,  # Maximum allowed by eBay APIs
            'offset': 0
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listings': data.get('inventoryItems', []),
                'total': data.get('total', 0),
                'note': 'Using OAuth 2.0 Inventory API'
            }
        elif response.status_code == 403:
            # Try Fulfillment API as fallback
            return get_ebay_fulfillment_oauth(access_token, api_base_url)
        else:
            return {
                'success': False,
                'error': 'OAuth Inventory API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'OAuth API error: {}'.format(str(e))
        }

def get_ebay_fulfillment_oauth(access_token, api_base_url):
    """
    Try Fulfillment API with OAuth token
    """
    try:
        url = "{}/sell/fulfillment/v1/order".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        params = {
            'limit': 200,
            'offset': 0
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listings': data.get('orders', []),
                'total': data.get('total', 0),
                'note': 'Using OAuth 2.0 Fulfillment API'
            }
        else:
            # Final fallback to Browse API
            return get_ebay_browse_oauth(access_token, api_base_url)
            
    except Exception as e:
        return {
            'success': False,
            'error': 'OAuth Fulfillment API error: {}'.format(str(e))
        }

def get_ebay_browse_oauth(access_token, api_base_url):
    """
    Try Browse API with OAuth token as final fallback
    """
    try:
        url = "{}/buy/browse/v1/item_summary/search".format(api_base_url)
        
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        params = {
            'q': '*',  # Search for all items
            'limit': 200,
            'offset': 0,
            'filter': 'conditionIds:{1000|1500|2000|2500|3000|4000|5000}'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listings': data.get('itemSummaries', []),
                'total': data.get('total', 0),
                'note': 'Using OAuth 2.0 Browse API - may show all items, not just yours'
            }
        else:
            return {
                'success': False,
                'error': 'OAuth Browse API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'OAuth Browse API error: {}'.format(str(e))
        }

def get_ebay_listing_details(listing_id):
    """
    Get detailed information for a specific eBay listing
    """
    try:
        # First try to get OAuth token
        token_result = get_valid_ebay_token()
        
        if token_result['success']:
            # Use OAuth 2.0 token
            api_base_url = app.config.get('EBAY_API_BASE_URL', 'https://api.ebay.com')
            user_token = token_result['access_token']
        else:
            # Fallback to legacy token
            user_token = app.config.get('EBAY_USER_TOKEN')
            api_base_url = app.config.get('EBAY_API_BASE_URL', 'https://api.ebay.com')
        
        if not user_token or user_token == 'YOUR_EBAY_USER_TOKEN_HERE':
            return {
                'success': False,
                    'error': 'eBay authentication required. Please authenticate with eBay OAuth or configure a legacy token.',
                    'needs_oauth': True
            }
        
        # eBay API endpoint for getting listing details
        url = "{}/sell/inventory/v1/inventory_item/{}".format(api_base_url, listing_id)
        
        headers = {
            'Authorization': 'Bearer {}'.format(user_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'listing': data
            }
        else:
            return {
                'success': False,
                'error': 'eBay API error: {} - {}'.format(response.status_code, response.text)
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'Error fetching listing details: {}'.format(str(e))
        }

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Get client IP address - handle both local development and production
        if 'HTTP_X_FORWARDED_FOR' in request.environ:
            # Production environment with proxy/load balancer
            addr = request.environ['HTTP_X_FORWARDED_FOR'].split(',')
            client_ip = addr[0].strip()
        else:
            # Local development environment
            client_ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
        
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        msg = function.login_data(username=username, password=password, ip=client_ip)
        if 'loggedin' in session:
            # Redirect to the next page if specified, otherwise go to index
            next_page = request.form.get('next') or request.args.get('next')
            if next_page:
                # Extract only the path and query string from the URL
                try:
                    from urllib.parse import urlparse
                except ImportError:
                    from urlparse import urlparse
                parsed = urlparse(next_page)
                if parsed.netloc:  # If it's a full URL, extract just the path
                    next_page = parsed.path
                    if parsed.query:
                        next_page += '?' + parsed.query
                # Handle relative paths
                elif not next_page.startswith('/'):
                    next_page = '/' + next_page
                return redirect(next_page)
            return redirect(url_for('index'))    
    return render_template('login.html', msg=msg)

@app.route('/google-login')
def google_login():
    """Initiate Google OAuth login"""
    # Generate state parameter for security
    state = hashlib.sha256(os.urandom(32)).hexdigest()
    session['oauth_state'] = state
    
    # Check if this is a mobile request
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile_request = 'gsaleapp' in user_agent or 'mobile' in request.args
    
    # Store mobile flag in session for callback
    if is_mobile_request:
        session['is_mobile_oauth'] = True
    
    # Always use web redirect URI for Google OAuth compliance
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        redirect_uri = 'http://127.0.0.1:5000/google-callback'
    else:
        redirect_uri = 'https://gsale.levimylesllc.com/google-callback'
    
    google_auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        'client_id={}&'
        'response_type=code&'
        'scope=openid%20email%20profile&'
        'redirect_uri={}&'
        'state={}&'
        'prompt=select_account'
    ).format(
        app.config['GOOGLE_CLIENT_ID'],
        redirect_uri,
        state
    )
    
    return redirect(google_auth_url)

@app.route('/mobile_oauth_success')
def mobile_oauth_success():
    """Direct route for mobile OAuth success page"""
    if 'loggedin' in session and session['loggedin']:
        return render_template('mobile_oauth_success.html', 
                             username=session.get('username', 'User'))
    else:
        return render_template('mobile_oauth_error.html', 
                             error='Not authenticated'), 401

# Temporary storage for session tokens (in production, use Redis or database)
mobile_sessions = {}

@app.route('/mobile_session_exchange', methods=['POST'])
def mobile_session_exchange():
    """Exchange mobile session token for session information"""
    data = request.get_json()
    if not data or 'session_token' not in data:
        return jsonify({'success': False, 'error': 'Missing session token'}), 400
    
    session_token = data['session_token']
    
    # Look up the session information by token
    if session_token in mobile_sessions:
        session_info = mobile_sessions[session_token]
        
        # Remove the token after use (one-time use)
        del mobile_sessions[session_token]
        
        return jsonify({
            'success': True,
            'session_cookie': session_info['session_cookie'],
            'username': session_info['username'],
            'user_id': session_info.get('user_id'),
            'is_admin': session_info.get('is_admin', False)
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid or expired session token'}), 401

@app.route('/google-callback', methods=['GET', 'POST'])
def google_callback():
    """Handle Google OAuth callback"""
    # Check if this is a mobile request based on session flag
    is_mobile_request = session.get('is_mobile_oauth', False)
    
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        flash('Invalid state parameter. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        error_msg = 'Authorization code not received.'
        if is_mobile_request:
            return render_template('mobile_oauth_error.html', error=error_msg)
        else:
            flash(error_msg, 'error')
            return redirect(url_for('login'))
    
    try:
        # Always use web redirect URI for Google OAuth compliance
        if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
            redirect_uri = 'http://127.0.0.1:5000/google-callback'
        else:
            redirect_uri = 'https://gsale.levimylesllc.com/google-callback'
        
        # Exchange code for tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': app.config['GOOGLE_CLIENT_ID'],
            'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info from Google
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': "Bearer {}".format(tokens['access_token'])}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        
        # Extract user data
        google_id = user_info['id']
        email = user_info['email']
        name = user_info.get('name', email)
        picture = user_info.get('picture')
        
        # Check if email exists in accounts table
        existing_user = get_data.get_user_by_email(email)
        
        if not existing_user:
            # Record the access attempt for new users only
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO access_attempts (email, successful, attempt_time) VALUES (%s, %s, NOW())', (email, False))
                mysql.connection.commit()
                cursor.close()
            except Exception as e:
                print("Error recording access attempt: {}".format(e))
            
            # Create new user account
            print("Creating new account for {}".format(email))
            user_id = set_data.create_user_account(email, name, google_id, picture)
            if not user_id:
                error_msg = 'Failed to create user account. Please try again.'
                if is_mobile_request:
                    return render_template('mobile_oauth_error.html', error=error_msg)
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('login'))
        else:
            user_id = existing_user['id']
            user = existing_user
            
            # Update Google ID if not set
            if not existing_user.get('google_id'):
                set_data.update_user_google_id(user_id, google_id)
        
        # Log user in
        session['loggedin'] = True
        session['id'] = user_id
        session['username'] = user.get('name', email) if 'user' in locals() else name
        session['email'] = email
        session['is_admin'] = user.get('is_admin', False) if 'user' in locals() else False
        session['group_id'] = user.get('group_id') if 'user' in locals() else None  # Store group_id for group-based access
        
        # Clear OAuth session data
        session.pop('oauth_state', None)
        session.pop('is_mobile_oauth', None)
        
        # Handle response based on request type
        if is_mobile_request:
            # For mobile, show success page with instructions to return to app
            # Generate a session token that represents the current session
            try:
                import secrets
                session_token = secrets.token_urlsafe(32)
            except ImportError:
                import uuid
                import base64
                session_token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
            
            # Store session information with the token for later retrieval
            mobile_sessions[session_token] = {
                'session_cookie': app.session_interface.get_signing_serializer(app).dumps(dict(session)),
                'username': session['username'],
                'user_id': session.get('id'),
                'is_admin': session.get('is_admin', False)
            }
            
            return render_template('mobile_oauth_success.html', 
                                 username=session['username'],
                                 session_token=session_token)
        else:
            # For web, redirect to home or next page
            flash('Login successful!', 'success')
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
            
    except Exception as e:
        print("OAuth error: {}".format(e))
        error_msg = 'Authentication failed: {}'.format(str(e))
        
        # Clear OAuth session data on error
        session.pop('oauth_state', None)
        session.pop('is_mobile_oauth', None)
        
        if is_mobile_request:
            return render_template('mobile_oauth_error.html', error=error_msg)
        else:
            flash(error_msg, 'error')
            return redirect(url_for('login'))

@app.route('/ebay-login')
def ebay_login():
    """Initiate eBay OAuth login"""
    try:
        # Generate OAuth URL
        oauth_result = get_ebay_oauth_url()
        
        if oauth_result['success']:
            return redirect(oauth_result['auth_url'])
        else:
            flash(f'eBay OAuth error: {oauth_result["error"]}', 'error')
            return redirect(url_for('admin_panel'))
            
    except Exception as e:
        flash(f'eBay OAuth error: {str(e)}', 'error')
        return redirect(url_for('admin_panel'))

@app.route('/ebay-callback', methods=['GET', 'POST'])
def ebay_callback():
    """Handle eBay OAuth callback"""
    try:
        # Get the state parameter from the request
        request_state = request.args.get('state')
        session_state = session.get('ebay_oauth_state')
        
        # Debug: Print state parameters for troubleshooting
        print(f"DEBUG: eBay OAuth Callback")
        print(f"  Request State: {request_state}")
        print(f"  Session State: {session_state}")
        print(f"  States Match: {request_state == session_state}")
        
        # Verify state parameter (eBay sometimes doesn't return it)
        if not request_state or not session_state or request_state != session_state:
            print(f"DEBUG: State validation failed")
            print(f"  Request State: {request_state}")
            print(f"  Session State: {session_state}")
            print(f"  Request State Length: {len(request_state) if request_state else 0}")
            print(f"  Session State Length: {len(session_state) if session_state else 0}")
            
            # eBay sometimes doesn't return the state parameter, so we'll proceed anyway
            if not request_state:
                print(f"DEBUG: No state parameter returned by eBay - proceeding anyway")
                # Continue with OAuth flow
            elif request_state and len(request_state) == 64:  # Valid state format
                print(f"DEBUG: Allowing OAuth to proceed despite state mismatch (debug mode)")
                # Continue with OAuth flow
            else:
                flash('Invalid state parameter. Please try again.', 'error')
                return redirect(url_for('settings_ebay_listings'))
        
        # Debug: Print all request parameters
        print(f"DEBUG: All request parameters:")
        for key, value in request.args.items():
            print(f"  {key}: {value}")
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error_msg = request.args.get('error', 'Authorization code not received.')
            print(f"DEBUG: No authorization code received. Error: {error_msg}")
            flash(f'eBay OAuth error: {error_msg}', 'error')
            return redirect(url_for('settings_ebay_listings'))
        
        print(f"DEBUG: Authorization code received: {code[:20]}...")
        
        # Exchange code for tokens
        token_result = exchange_ebay_code_for_token(code)
        
        if token_result['success']:
            flash('eBay OAuth authentication successful!', 'success')
            return redirect(url_for('settings_ebay_listings'))
        else:
            flash(f'eBay OAuth error: {token_result["error"]}', 'error')
            return redirect(url_for('settings_ebay_listings'))
            
    except Exception as e:
        print(f"DEBUG: eBay OAuth callback exception: {str(e)}")
        flash(f'eBay OAuth error: {str(e)}', 'error')
        return redirect(url_for('settings_ebay_listings'))

@app.route('/ebay-logout')
def ebay_logout():
    """Clear eBay OAuth tokens for current user"""
    try:
        # Clear eBay OAuth session data
        session.pop('ebay_access_token', None)
        session.pop('ebay_refresh_token', None)
        session.pop('ebay_token_expires', None)
        session.pop('ebay_oauth_state', None)
        
        # Clear tokens from database for current user
        user_id = session.get('id')
        if user_id:
            try:
                if not mysql.connection:
                    mysql.connect()
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM ebay_tokens WHERE user_id = %s", (user_id,))
                mysql.connection.commit()
            except Exception as db_error:
                print(f"Error clearing database tokens: {db_error}")
        
        flash('eBay OAuth tokens cleared successfully!', 'success')
        return redirect(url_for('settings_ebay_listings'))
        
    except Exception as e:
        flash(f'Error clearing eBay tokens: {str(e)}', 'error')
        return redirect(url_for('settings_ebay_listings'))

@app.route('/debug/ebay-oauth-url')
def debug_ebay_oauth_url():
    """Debug endpoint to test OAuth URL generation"""
    try:
        oauth_result = get_ebay_oauth_url()
        if oauth_result['success']:
            return f"""
            <h3>eBay OAuth URL Debug</h3>
            <p><strong>Status:</strong> Success</p>
            <p><strong>Generated URL:</strong></p>
            <textarea rows="10" cols="100" readonly>{oauth_result['auth_url']}</textarea>
            <p><strong>State:</strong> {oauth_result['state']}</p>
            <p><strong>Config Values:</strong></p>
            <ul>
                <li>Client ID: {app.config.get('EBAY_CLIENT_ID', 'NOT SET')}</li>
                <li>Redirect URI: {app.config.get('EBAY_REDIRECT_URI', 'NOT SET')}</li>
                <li>Sandbox Mode: {app.config.get('EBAY_SANDBOX_MODE', 'NOT SET')}</li>
                <li>Scope: {app.config.get('EBAY_OAUTH_SCOPE', 'NOT SET')[:100]}...</li>
            </ul>
            <p><a href="{oauth_result['auth_url']}" target="_blank">Test OAuth URL</a></p>
            """
        else:
            return f"<h3>Error:</h3><p>{oauth_result['error']}</p>"
    except Exception as e:
        return f"<h3>Exception:</h3><p>{str(e)}</p>"

@app.route('/api/ebay-oauth-status')
def api_ebay_oauth_status():
    """API endpoint to check eBay OAuth status"""
    try:
        # Debug: Print session info
        print(f"DEBUG: OAuth status check:")
        print(f"  Session ID: {session.get('_id', 'No session ID')}")
        print(f"  Session keys: {list(session.keys())}")
        
        token_result = get_valid_ebay_token()
        
        if token_result['success']:
            token_expires = session.get('ebay_token_expires')
            expires_at = None
            if token_expires:
                expires_at = token_expires.strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({
                'success': True,
                'has_token': True,
                'expires_at': expires_at
            })
        else:
            return jsonify({
                'success': True,
                'has_token': False,
                'error': token_result.get('error', 'No token available')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ebay-refresh-token', methods=['POST'])
def api_ebay_refresh_token():
    """API endpoint to refresh eBay OAuth token"""
    try:
        refresh_token = session.get('ebay_refresh_token')
        
        if not refresh_token:
            return jsonify({
                'success': False,
                'error': 'No refresh token available'
            })
        
        refresh_result = refresh_ebay_token(refresh_token)
        
        if refresh_result['success']:
            return jsonify({
                'success': True,
                'message': 'Token refreshed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': refresh_result['error']
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ebay-force-refresh', methods=['POST'])
def api_ebay_force_refresh():
    """API endpoint to force refresh all eBay tokens immediately"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT user_id, access_token, refresh_token, expires_at
            FROM ebay_tokens
            WHERE refresh_token IS NOT NULL
        """)
        
        tokens_to_refresh = cur.fetchall()
        refreshed_count = 0
        failed_count = 0
        
        for token_data in tokens_to_refresh:
            user_id, access_token, refresh_token, expires_at = token_data
            
            refresh_result = refresh_ebay_token(refresh_token)
            
            if refresh_result['success']:
                store_ebay_tokens_in_db(
                    refresh_result['access_token'],
                    refresh_result.get('refresh_token', refresh_token),
                    datetime.now() + timedelta(seconds=refresh_result.get('expires_in', 7200)),
                    user_id
                )
                refreshed_count += 1
            else:
                failed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Force refresh completed. {refreshed_count} tokens refreshed, {failed_count} failed.',
            'refreshed_count': refreshed_count,
            'failed_count': failed_count
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ebay-refresh-status', methods=['GET'])
def api_ebay_refresh_status():
    """API endpoint to check the status of automatic token refresh"""
    try:
        cur = mysql.connection.cursor()
        
        # Get token count and expiration info
        cur.execute("""
            SELECT 
                COUNT(*) as total_tokens,
                COUNT(CASE WHEN refresh_token IS NOT NULL THEN 1 END) as tokens_with_refresh,
                COUNT(CASE WHEN expires_at <= DATE_ADD(NOW(), INTERVAL 20 MINUTE) THEN 1 END) as tokens_expiring_soon,
                MIN(expires_at) as earliest_expiration,
                MAX(expires_at) as latest_expiration
            FROM ebay_tokens
        """)
        
        stats = cur.fetchone()
        
        return jsonify({
            'success': True,
            'background_refresh_active': _background_refresh_started,
            'token_stats': {
                'total_tokens': stats[0],
                'tokens_with_refresh': stats[1],
                'tokens_expiring_soon': stats[2],
                'earliest_expiration': stats[3].isoformat() if stats[3] else None,
                'latest_expiration': stats[4].isoformat() if stats[4] else None
            },
            'refresh_schedule': 'Every 15 minutes',
            'refresh_threshold': '20 minutes before expiration'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ebay-debug-refresh', methods=['POST'])
def api_ebay_debug_refresh():
    """Debug endpoint to test token refresh with detailed logging"""
    try:
        print("DEBUG: Starting debug refresh process...")
        
        # First check if the table exists and has any data
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES LIKE 'ebay_tokens'")
        table_exists = cur.fetchone()
        
        print(f"DEBUG: Table exists check result: {table_exists}")
        
        if not table_exists:
            return jsonify({
                'success': False,
                'error': 'ebay_tokens table does not exist. Please run the SQL migration first.',
                'debug_info': {
                    'table_exists': False,
                    'suggestion': 'Run the SQL script: sql/create_ebay_tokens_table.sql'
                }
            })
        
        # Try to get token count, but don't fail if there's an issue
        try:
            cur.execute("SELECT COUNT(*) FROM ebay_tokens")
            count_result = cur.fetchone()
            print(f"DEBUG: Count result type: {type(count_result)}, value: {count_result}")
            
            # Handle different MySQL result formats
            if count_result is None:
                total_count = 0
            elif isinstance(count_result, (tuple, list)) and len(count_result) > 0:
                total_count = count_result[0]
            elif isinstance(count_result, dict):
                total_count = count_result.get('COUNT(*)', 0)
            else:
                total_count = int(count_result) if count_result else 0
                
            print(f"DEBUG: Total tokens in database: {total_count}")
        except Exception as count_error:
            print(f"DEBUG: Error getting count: {count_error}")
            total_count = "unknown"
        
        # Check if we have tokens in database
        cur.execute("""
            SELECT user_id, access_token, refresh_token, expires_at, updated_at
            FROM ebay_tokens
            WHERE refresh_token IS NOT NULL
            ORDER BY updated_at DESC
        """)
        
        tokens_in_db = cur.fetchall()
        print(f"DEBUG: Found {len(tokens_in_db)} tokens with refresh tokens in database")
        
        # Debug: Print the actual data returned
        for i, token_data in enumerate(tokens_in_db):
            print(f"DEBUG: Token {i}: {token_data}")
        
        if not tokens_in_db:
            return jsonify({
                'success': False,
                'error': 'No tokens with refresh tokens found in database. Please authenticate with eBay first.',
                'debug_info': {
                    'total_tokens': total_count,
                    'tokens_with_refresh': len(tokens_in_db),
                    'session_tokens': {
                        'access_token': bool(session.get('ebay_access_token')),
                        'refresh_token': bool(session.get('ebay_refresh_token')),
                        'expires_at': session.get('ebay_token_expires')
                    }
                }
            })
        
        debug_results = []
        
        for token_data in tokens_in_db:
            print(f"DEBUG: Token data type: {type(token_data)}, value: {token_data}")
            
            # Handle both dict and tuple formats
            if isinstance(token_data, dict):
                user_id = token_data.get('user_id')
                access_token = token_data.get('access_token')
                refresh_token = token_data.get('refresh_token')
                expires_at = token_data.get('expires_at')
                updated_at = token_data.get('updated_at')
            else:
                # Assume tuple format
                user_id, access_token, refresh_token, expires_at, updated_at = token_data
            
            print(f"DEBUG: Testing refresh for user {user_id}")
            print(f"DEBUG: Current token expires at: {expires_at}")
            print(f"DEBUG: Last updated at: {updated_at}")
            
            # Test the refresh
            refresh_result = refresh_ebay_token(refresh_token)
            
            # Handle both string and datetime formats
            def format_datetime(dt):
                if dt is None:
                    return None
                if isinstance(dt, str):
                    return dt
                return dt.isoformat()
            
            debug_info = {
                'user_id': user_id,
                'refresh_success': refresh_result['success'],
                'error': refresh_result.get('error'),
                'old_expires_at': format_datetime(expires_at),
                'old_updated_at': format_datetime(updated_at)
            }
            
            if refresh_result['success']:
                # Check if database was actually updated
                cur.execute("""
                    SELECT expires_at, updated_at
                    FROM ebay_tokens
                    WHERE user_id = %s
                """, (user_id,))
                
                updated_token = cur.fetchone()
                if updated_token:
                    print(f"DEBUG: Updated token type: {type(updated_token)}, value: {updated_token}")
                    
                    # Handle both dict and tuple formats
                    if isinstance(updated_token, dict):
                        new_expires_at = updated_token.get('expires_at')
                        new_updated_at = updated_token.get('updated_at')
                    else:
                        new_expires_at = updated_token[0]
                        new_updated_at = updated_token[1]
                    
                    debug_info['new_expires_at'] = format_datetime(new_expires_at)
                    debug_info['new_updated_at'] = format_datetime(new_updated_at)
                    
                    # Compare timestamps properly
                    old_updated = updated_at
                    new_updated = new_updated_at
                    
                    # Convert to datetime if they're strings
                    if isinstance(old_updated, str):
                        from datetime import datetime
                        old_updated = datetime.fromisoformat(old_updated.replace('Z', '+00:00'))
                    if isinstance(new_updated, str):
                        from datetime import datetime
                        new_updated = datetime.fromisoformat(new_updated.replace('Z', '+00:00'))
                    
                    debug_info['database_updated'] = new_updated > old_updated
                else:
                    debug_info['database_updated'] = False
                    debug_info['error'] = 'Token not found after refresh'
            else:
                debug_info['database_updated'] = False
            
            debug_results.append(debug_info)
        
        return jsonify({
            'success': True,
            'message': 'Debug refresh completed',
            'debug_results': debug_results,
            'config_check': {
                'client_id_configured': bool(app.config.get('EBAY_CLIENT_ID')),
                'client_secret_configured': bool(app.config.get('EBAY_CLIENT_SECRET')),
                'oauth_scope_configured': bool(app.config.get('EBAY_OAUTH_SCOPE')),
                'sandbox_mode': app.config.get('EBAY_SANDBOX_MODE', False)
            },
            'recommendations': {
                're_authenticate': 'If refresh tokens are invalid, you need to re-authenticate with eBay',
                'clear_old_tokens': 'Consider clearing old tokens from database',
                'check_credentials': 'Verify eBay Client ID and Secret are correct'
            }
        })
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/ebay-clear-tokens', methods=['POST'])
def api_ebay_clear_tokens():
    """Clear all eBay tokens from database and session"""
    try:
        # Clear from database
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM ebay_tokens")
        mysql.connection.commit()
        
        # Clear from session
        session.pop('ebay_access_token', None)
        session.pop('ebay_refresh_token', None)
        session.pop('ebay_token_expires', None)
        
        return jsonify({
            'success': True,
            'message': 'All eBay tokens cleared from database and session. Please re-authenticate with eBay.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/logout')
def logout():
    # Get the current page from referrer, but handle edge cases
    next_page = request.referrer
    
    # If no referrer or referrer is the logout page itself, use a default
    if not next_page or '/logout' in next_page or next_page.endswith('/'):
        next_page = url_for('index')
    
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    
    # Redirect to login with the stored page as the next parameter
    return redirect(url_for('login', next=next_page))

@app.route('/logout/<path:next_page>')
def logout_with_redirect(next_page):
    """Logout and redirect to a specific page after login"""
    
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    
    # Decode the URL-encoded next_page parameter
    decoded_next_page = unquote(next_page)
    
    # Handle the "index" parameter specially
    if decoded_next_page == 'index':
        decoded_next_page = '/'
    else:
        # Add leading slash for non-index pages
        if not decoded_next_page.startswith('/'):
            decoded_next_page = '/' + decoded_next_page
    
    # Redirect to login with the specified page as the next parameter
    return redirect(url_for('login', next=decoded_next_page))



@app.route('/')
@login_required
def index():
    items = []
    years = get_data.get_years()
   
    for value in years:
        item = get_data.get_profit(value['year'])
        items.append(item)
    return render_template('index.html', items=items)

@app.route('/reports/profit',methods=["GET", "POST"])
@login_required
def reports_profit():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        
        # Check cache first
        cache_params = {
            'type': details['type'],
            'date': str(details['date']),
            'month': details['month'],
            'year': details['year'],
            'day': details.get('day', '')
        }
        
        cached_data = get_cached_report('profit', cache_params)
        if cached_data:
            return render_template('reports_profit.html', 
                                form=form, 
                                sold_dates=cached_data['sold_dates'], 
                                purchased_dates=cached_data['purchased_dates'],
                                type_value=details['type'])
        
        if not details['type'] == '3':
            start_date, end_date = function.set_dates(details)
            sold_dates = get_data.get_group_sold_from_date(start_date, end_date)
            purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        else:
            sold_dates = get_data.get_group_sold_from_day(details['day'])
            purchased_dates = get_data.get_purchased_from_day(details['day'],details['year'])
        
        # Cache the results
        cache_report('profit', cache_params, {
            'sold_dates': sold_dates,
            'purchased_dates': purchased_dates
        })
        
        return render_template('reports_profit.html', 
                            form=form, 
                            sold_dates=sold_dates, 
                            purchased_dates=purchased_dates,
                            type_value=details['type'])
    return render_template('reports_profit.html', form=form)


@app.route('/reports/sales',methods=["GET", "POST"])
@login_required
def reports_sale():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        if not details['type'] == '3':
            start_date, end_date = function.set_dates(details)
            sold_dates = get_data.get_sold_from_date(start_date, end_date)
        else:
            sold_dates = get_data.get_sold_from_day(details['day'])
        return render_template('reports_sales.html', form=form, sold_dates=sold_dates,type_value=details['type'])
    return render_template('reports_sales.html', form=form)

@app.route('/reports/purchases',methods=["GET", "POST"])
@login_required
def reports_purchases():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form

        if not details['type'] == '3':
            start_date, end_date = function.set_dates(details)
            purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        else:
            purchased_dates = get_data.get_purchased_from_day(details['day'])

        return render_template('reports_purchases.html', form=form, purchased_dates=purchased_dates, type_value=details['type'])
    return render_template('reports_purchases.html', form=form)

@app.route('/reports/categories',methods=["GET", "POST"])
@login_required
def reports_categories():
    form = ReportsForm()

    categories = get_data.get_all_from_categories()
    category_counts = get_data.get_category_item_counts()
    form.category.choices = [(category['id'], category['type']) for category in categories]

    if request.method == "POST":
        details = request.form
        item_categories = get_data.get_list_of_items_with_categories(details['category'])
        return render_template('reports_item_categories.html', form=form, item_categories=item_categories, category_counts=category_counts, now=datetime.now().date())
    return render_template('reports_item_categories.html', form=form, category_counts=category_counts)



@app.route('/reports/locations',methods=["GET", "POST"])
@login_required
def reports_locations():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        locations = get_data.get_location_from_date(start_date, end_date)
        return render_template('reports_locations.html', form=form, locations=locations)
    return render_template('reports_locations.html', form=form)

@app.route('/reports/city',methods=["GET", "POST"])
@login_required
def reports_city():
    form = CityReportForm()
    
    # Get all available states and populate the dropdown
    states = get_data.get_all_states()
    form.state.choices = [(state['state_name'], "{} ({} purchases, ${:.2f})".format(state['state_name'], state['purchase_count'], float(state['total_spent']))) for state in states]
    
    # Get all available years and populate the dropdown
    years = get_data.get_years()
    form.year.choices = [('all', 'All Years')] + [(str(year['year']), str(year['year'])) for year in years]
    
    # Initially populate cities with empty choices (will be populated by JavaScript when state is selected)
    form.city.choices = [('', 'Select a city...')]

    if request.method == "POST":
        details = request.form
        state = details.get('state', '').strip()
        city = details.get('city', '').strip()
        year = details.get('year', 'all')
        
        if city:
            purchases = get_data.get_purchases_by_city(city, year)
            summary = get_data.get_city_summary(city, year)
            return render_template('reports_city.html', form=form, purchases=purchases, summary=summary, city=city, selected_year=year, selected_state=state)
        else:
            flash('Please select a city', 'error')
    
    return render_template('reports_city.html', form=form)

@app.route('/reports/api/cities-by-state/<state>')
@login_required
def api_cities_by_state(state):
    """API endpoint to get cities for a specific state"""
    try:
        cities = get_data.get_cities_by_state(state)
        return jsonify({
            'success': True,
            'cities': cities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    return render_template('reports_city.html', form=form)

# Neighborhood Reports
@app.route('/reports/neighborhood', methods=["GET", "POST"])
@login_required
def reports_neighborhood():
    # Get all neighborhoods for the current user
    neighborhoods = get_data.get_user_neighborhoods()
    
    # Get selected filters from request
    selected_state = request.form.get('state', '') if request.method == "POST" else ''
    selected_city = request.form.get('city', '') if request.method == "POST" else ''
    
    # Get unique states and cities that exist in the data
    state_choices = sorted(list(set([n.get('state') for n in neighborhoods if n.get('state')])))
    city_choices = sorted(list(set([n.get('city') for n in neighborhoods if n.get('city')])))
    
    # Filter neighborhoods based on state and city
    filtered_neighborhoods = []
    for neighborhood in neighborhoods:
        # Apply state filter
        if selected_state and neighborhood.get('state') != selected_state:
            continue
        # Apply city filter
        if selected_city and neighborhood.get('city') != selected_city:
            continue
        filtered_neighborhoods.append(neighborhood)
    
    # Get neighborhood data
    neighborhood_data = []
    for neighborhood in filtered_neighborhoods:
        sales_data = get_data.get_neighborhood_sales_data(neighborhood['id'])
        neighborhood_data.append({
            'neighborhood': neighborhood,
            'sales_data': sales_data
        })
    
    return render_template('reports_neighborhood.html', 
                         neighborhoods=neighborhood_data, 
                         all_neighborhoods=neighborhoods,  # Pass all neighborhoods for JavaScript
                         state_choices=state_choices,
                         city_choices=city_choices,
                         selected_state=selected_state,
                         selected_city=selected_city)

#Data Section
@app.route('/groups/create',methods=["POST","GET"])
@login_required
def group_add():
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        print("Received form data: {}".format(details))
        
        # Check for required fields
        if 'date' not in details or 'name' not in details:
            return jsonify({
                'success': False,
                'message': 'Missing required fields: date and name are required'
            }), 400
        
        group_name = "%s-%s" % (details['date'],details['name'])
        
        # Handle image upload - make it optional for API calls
        image_id = ""
        if 'image' in request.files and request.files['image'].filename:
            try:
                image_id = files.upload_image(request.files['image'])
            except Exception as e:
                print("Error uploading image: {}".format(e))
                image_id = ""
        else:
            # No image provided, use empty string
            image_id = ""
        
        try:
            group_id = set_data.set_group_add(group_name, details, image_id)
            return redirect(url_for('group_detail',group_id=group_id))
        except KeyError as e:
            return jsonify({
                'success': False,
                'message': 'Missing required field: {}'.format(str(e))
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error creating group: {}'.format(str(e))
            }), 500
    return render_template('groups_add.html', form=form, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'], neighborhoods=get_data.get_user_neighborhoods())

@app.route('/display/<filename>')
@login_required
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)










@app.route('/groups/modify',methods=["POST","GET"])
@login_required
def modify_group():
    id = request.args.get('group_id', type = str)
    group_id = get_data.get_data_from_group_list(id)

    form = GroupForm()

    if request.method == "POST":
        details = request.form
        if(request.files['image']):
            image_id = files.upload_image(request.files['image'])
        else:
            image_id = group_id[0]['image']
        set_data.set_group_modify(details, image_id)
        return redirect(url_for('group_detail',group_id=details['id']))
    return render_template('modify_group.html', group_id=group_id, form=form, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'], neighborhoods=get_data.get_user_neighborhoods())

@app.route('/items/mark_sold',methods=["POST","GET"])
@login_required
def mark_sold():
    id = request.args.get('item', type = str)
    sold = request.args.get('sold', type = str)
    # Convert string to integer for validation
    sold_int = int(sold) if sold in ['0', '1'] else None
    set_data.set_mark_sold(id, sold_int)    
    return redirect(url_for('describe_item',item=id))

@app.route('/items/bought',methods=["POST","GET"])
@login_required
def bought_items():
    group_id = request.args.get('group', type = str)
    
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()

    form = PurchaseForm()

    form.group.choices = [(group['id'], group['name']) for group in groups]
    
    # No need to initialize FieldList since we're using HTML fallback

    if group_id:
        group_data = get_data.get_all_from_group(group_id)
        if not group_data:
            flash('Group not found or access denied.', 'error')
            return redirect(url_for('index'))
        form.group.data = group_id
        form.list_date.data = group_data['date']

    if request.method == "POST":
        details = request.form.to_dict()
        
        group_data = get_data.get_all_from_group(details['group'])
        if not group_data:
            flash('Group not found or access denied.', 'error')
            return redirect(url_for('index'))
        
        # Process the new form structure
        set_data.set_bought_items_improved(details)
        return redirect(url_for('group_detail',group_id=group_data['id']))
    
    return render_template('items_purchased.html', form=form, categories=categories)

@app.route('/items/modify',methods=["POST","GET"])
@login_required
def modify_items():
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()
    id = request.args.get('item', type = str)
    return_to = request.args.get('return_to', type = str)
    item = get_data.get_data_for_item_describe(id)
    
    # Check if item exists and belongs to current user
    if not item:
        flash('Item not found or access denied.', 'error')
        return redirect(url_for('index'))
    
    sale = get_data.get_data_from_sale(id)

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = item[0]['group_id']

    form.category.choices = [(category['id'], category['type']) for category in categories]
    form.category.data = item[0]['category_id']

    form.returned.choices = [(0, 'False'), (1, "True")]
    form.returned.data = item[0]['returned']

    if request.method == "POST":
        details = request.form
        set_data.set_items_modify(details)
        set_data.set_sale_data(details)
        
        # Redirect back to the appropriate page based on return_to parameter
        return_to_from_form = details.get('return_to')
        if return_to_from_form == 'group_detail' or return_to == 'group_detail':
            flash('Item updated successfully!', 'success')
            return redirect(url_for('group_detail', group_id=item[0]['group_id']))
        else:
            flash('Item updated successfully!', 'success')
            return redirect(url_for('describe_item',item=id))
    
    return render_template('modify_item.html', form=form, item=item, sale=sale, return_to=return_to)

@app.route('/items/modify_ajax', methods=['POST'])
@login_required
def modify_items_ajax():
    try:
        details = request.form
        item_id = details.get('id')
        
        # Check if item exists and belongs to current user
        item = get_data.get_data_for_item_describe(item_id)
        if not item:
            return jsonify({
                'success': False,
                'message': 'Item not found or access denied.'
            }), 404
        
        # Update item data
        set_data.set_items_modify(details)
        set_data.set_sale_data(details)
        
        return jsonify({
            'success': True,
            'message': 'Item updated successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating item: {}'.format(str(e))
        }), 500

@app.route('/items/remove',methods=["POST","GET"])
@login_required
def items_remove():
    id = request.args.get('id', type = str)
    item=get_data.get_group_id(id)
    
    # Check if item exists and belongs to current user
    if not item:
        flash('Item not found or access denied.', 'error')
        return redirect(url_for('index'))
    
    set_data.remove_item_data(id)
    return redirect(url_for('group_detail',group_id=item['group_id']))


@app.route('/items/quick_sell',methods=["POST","GET"])
@login_required
def quick_sell():
    group_id = request.args.get('group', type = str)

    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]

    form.category.choices = [(category['id'], category['type']) for category in categories]

    if group_id:
        group_data = get_data.get_all_from_group(group_id)
        if not group_data:
            flash('Group not found or access denied.', 'error')
            return redirect(url_for('index'))
        form.group.data = group_id
        form.list_date.data = group_data['date']

    if request.method == "POST":
        details = request.form
        group_data = get_data.get_all_from_group(details['group'])
        if not group_data:
            flash('Group not found or access denied.', 'error')
            return redirect(url_for('index'))
        id = set_data.set_quick_sale(details)
        return redirect(url_for('describe_item',item=id))
    return render_template('quick_sell.html', form=form)

@app.route('/items/sold',methods=["POST","GET"])
@login_required
def sold_items():
    # Refresh eBay token if needed before processing
    refresh_token_if_needed()
    
    item_id = request.args.get('item', type = str)
    items = get_data.get_all_items_not_sold()

    form = SaleForm()
    form.id.choices = [(item['id'], item['name']) for item in items]
    form.id.data = item_id
    
    # Check if the selected item has an eBay item ID and fetch financial data
    ebay_price = None
    if item_id:
        item_data = get_data.get_data_for_item_describe(item_id)
        if item_data and item_data[0].get('ebay_item_id'):
            ebay_item_id = item_data[0]['ebay_item_id']
            
            # Get eBay financial data
            token_result = get_valid_ebay_token()
            if token_result['success']:
                user_token = token_result['access_token']
            else:
                user_token = app.config.get('EBAY_USER_TOKEN')
            
            if user_token and user_token != 'YOUR_EBAY_USER_TOKEN_HERE':
                transaction_data = get_item_transaction_details(user_token, ebay_item_id)
                
                if transaction_data['success']:
                    trans_data = transaction_data['transaction_data']
                    ebay_price = trans_data.get('net_earnings', 0)
                else:
                    ebay_price = None
    
    # Prepopulate form with eBay price only (shipping will be entered manually)
    if ebay_price is not None:
        form.price.data = str(round(float(ebay_price), 2))

    if request.method == "POST":
        details = request.form
        set_data.set_mark_sold(details['id'], 1)
        set_data.set_sale_data(details)
        return redirect(url_for('describe_item',item=details['id']))
    return render_template('items_sold.html', form=form)


@app.route('/api/ebay-item-data/<item_id>')
@login_required
def get_ebay_item_data(item_id):
    """API endpoint to fetch eBay financial data for a specific item"""
    try:
        # Get item data
        item_data = get_data.get_data_for_item_describe(item_id)
        if not item_data or not item_data[0].get('ebay_item_id'):
            return jsonify({
                'success': False,
                'message': 'No eBay item ID found for this item'
            })
        
        ebay_item_id = item_data[0]['ebay_item_id']
        
        # Get eBay financial data
        token_result = get_valid_ebay_token()
        if token_result['success']:
            user_token = token_result['access_token']
        else:
            user_token = app.config.get('EBAY_USER_TOKEN')
        
        if not user_token or user_token == 'YOUR_EBAY_USER_TOKEN_HERE':
            return jsonify({
                'success': False,
                'message': 'eBay authentication required'
            })
        
        # Fetch transaction details
        transaction_data = get_item_transaction_details(user_token, ebay_item_id)
        
        if transaction_data['success']:
            trans_data = transaction_data['transaction_data']
            return jsonify({
                'success': True,
                'ebay_data': {
                    'net_earnings': round(float(trans_data.get('net_earnings', 0)), 2),
                    'final_price': round(float(trans_data.get('final_price', 0)), 2),
                    'total_fees': round(float(trans_data.get('total_fees', 0)), 2)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Could not fetch eBay data: {transaction_data.get('error', 'Unknown error')}"
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching eBay data: {str(e)}'
        })

#List Section

@app.route('/groups/list', methods=["POST","GET"])
@login_required
def groups_list():
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        if details['listYear'] == 'All':
            date = "%-%-%"
        else:
            date = details['listYear'] + "-%-%"
    else:
        date = request.args.get('date', type = str)

    groups = get_data.get_all_from_group_and_items(date)
    return render_template('groups_list.html', groups=groups, form=form)

@app.route('/items/list', methods=["POST","GET"])
@login_required
def list_items():
    sold_date = request.args.get('sold_date', type = str)
    if sold_date is None:
        sold_date = "%"

    purchase_date = request.args.get('purchase_date', type = str)
    if purchase_date is None:
        purchase_date = "%"



    list_date = request.args.get('list_date', type = str)
    if list_date is None:
        list_date = "%"

    storage = request.args.get('storage', type = str)
    if storage is None:
        storage = "%"

    category_id = request.args.get('category_id', type = str)
    sold_status = request.args.get('sold_status', type = str)
    if sold_status is None:
        sold_status = "all"
    
    if category_id:
        # If category_id is provided, filter items by category and sold status
        items = get_data.get_list_of_items_by_category(category_id, sold_status)
    else:
        # Use the new sold status filtering function
        items = get_data.get_list_of_items_by_sold_status(sold_status, sold_date, purchase_date, list_date, storage)

    return render_template('items_list.html', 
                            items=items)

#Search Section
@app.route('/items/search', methods=["POST","GET"])
@login_required
def items_search():
    return render_template('items_search.html')

@app.route('/groups/search', methods=["POST","GET"])
@login_required
def groups_search():
    return render_template('groups_search.html')

#Describe Section
@app.route('/items/describe',methods=["POST","GET"])
@login_required
def describe_item():
    id = request.args.get('item', type = str)
    return_to = request.args.get('return_to', type = str)
    item = get_data.get_data_for_item_describe(id)
    
    # Check if item exists and belongs to current user
    if not item:
        flash('Item not found or access denied.', 'error')
        return redirect(url_for('index'))

    form = ButtonForm()
    form.button.label.text = "Sell Item"
    form.id.data = id

    remove = ButtonForm()
    remove.button.label.text = "Remove Item"
    remove.id.data = id

    modify = ButtonForm()
    modify.button.label.text = "Modify Item"
    modify.id.data = id

    availability = ButtonForm()
    if item[0]['sold']:
        availability.button.label.text = "Mark as Available"
    else:
        availability.button.label.text = "Mark as Sold"
    availability.id.data = id

    # Add return form
    return_form = ReturnItemForm()
    return_form.id.data = id
    if return_to:
        return_form.return_to.data = return_to

    if request.method == "POST":
        details = request.form
        if details['button'] == "Sell Item":
            return redirect(url_for('sold_items',item=details['id']))
        elif details['button'] == "Remove Item":
            return redirect(url_for('items_remove',id=details['id']))
        elif details['button'] == "Modify Item":
            # Pass return_to parameter to modify_items
            modify_url = url_for('modify_items', item=details['id'])
            if return_to:
                modify_url += '&return_to={}'.format(return_to)
            return redirect(modify_url)
        elif details['button'] == "Mark as Available":
            return redirect(url_for('mark_sold',item=details['id'],sold=0))
        elif details['button'] == "Mark as Sold":
            return redirect(url_for('mark_sold',item=details['id'],sold=1))
        
    category = get_data.get_category(item[0]['category_id'])
    item_sold = get_data.get_data_for_item_sold(id)
    return render_template('items_describe.html', 
                            item=item,
                            category=category,
                            sold=item_sold,
                            form=form,
                            remove=remove,
                            modify=modify,
                            availability=availability,
                            return_form=return_form,
                            return_to=return_to)

@app.route('/items/return', methods=["POST"])
@login_required
def return_item():
    item_id = request.form.get('id')
    returned_fee = request.form.get('returned_fee')
    return_to = request.form.get('return_to')
    
    if not item_id or not returned_fee:
        flash('Missing required information for return.', 'error')
        return redirect(url_for('describe_item', item=item_id))
    
    try:
        # Validate returned_fee is a valid number
        try:
            returned_fee = float(returned_fee)
            if returned_fee < 0:
                flash('Returned fee must be a positive number.', 'error')
                return redirect(url_for('describe_item', item=item_id))
        except ValueError:
            flash('Returned fee must be a valid number.', 'error')
            return redirect(url_for('describe_item', item=item_id))
        
        # Check if item exists and belongs to current user
        item = get_data.get_data_for_item_describe(item_id)
        if not item:
            flash('Item not found or access denied.', 'error')
            return redirect(url_for('index'))
        
        # Check if item is already returned
        if item[0]['returned']:
            flash('Item is already marked as returned.', 'error')
            return redirect(url_for('describe_item', item=item_id))
        
        # Mark item as returned and update sale table
        set_data.mark_item_returned(item_id, returned_fee)
        
        flash('Item marked as returned successfully!', 'success')
        
        # Redirect back to appropriate page
        if return_to == 'group_detail':
            return redirect(url_for('group_detail', group_id=item[0]['group_id']))
        else:
            return redirect(url_for('describe_item', item=item_id))
            
    except Exception as e:
        flash('Error processing return: {}'.format(str(e)), 'error')
        return redirect(url_for('describe_item', item=item_id))



@app.route('/groups/detail', methods=["POST","GET"])
@login_required
def group_detail():
    id = request.args.get('group_id', type = str)
    group_id = get_data.get_data_from_group_list(id)
    
    # Check if group exists and belongs to current user
    if not group_id:
        flash('Group not found or access denied.', 'error')
        return redirect(url_for('index'))
    
    items = get_data.get_data_from_item_groups(id)
    total_items = get_data.get_total_items_in_group(id)
    total_sold_items = get_data.get_total_items_in_group_sold(id)
    sold_price = get_data.get_group_profit(id)
    total_returned_fees = get_data.get_total_returned_fees_in_group(id)
    if not sold_price:
        sold_price = 0

    form = ButtonForm()
    form.button.label.text = "List Items"
    form.id.data = id

    quicksell = ButtonForm()
    quicksell.button.label.text = "Quick Sell"
    quicksell.id.data = id

    if request.method == "POST":
        details = request.form
        if details['button'] == "List Items":
            return redirect(url_for('bought_items',group=details['id']))
        elif details['button'] == "Quick Sell":
            return redirect(url_for('quick_sell',group=details['id']))

    # Get groups and categories for modal dropdowns
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()
    
    # Get neighborhoods for assignment dropdown
    neighborhoods = get_data.get_user_neighborhoods()
    
    # Get group creator information
    group_creator = get_data.get_group_creator(id)
    
    return render_template('groups_list_detail.html', 
                            group_id=group_id,
                            items=items,
                            total_items=total_items,
                            total_sold_items=total_sold_items,
                            sold_price=sold_price,
                            total_returned_fees=total_returned_fees,
                            form=form,
                            quicksell=quicksell,
                            groups=groups,
                            categories=categories,
                            neighborhoods=neighborhoods,
                            group_creator=group_creator)

@app.route('/groups/remove',methods=["POST","GET"])
@login_required
def group_remove():
    id = request.args.get('id', type = str)
    set_data.remove_group_data(id)
    return redirect(url_for('groups_list'))

@app.route('/groups/delete', methods=["POST"])
@login_required
def group_delete():
    """Delete a group and all its associated data"""
    group_id = request.form.get('group_id')
    
    if not group_id:
        flash('Group ID is required.', 'error')
        return redirect(url_for('groups_list'))
    
    try:
        # Check if user has permission to delete this group
        # For now, we'll allow any logged-in user to delete groups
        # You might want to add additional permission checks here
        
        # Delete the group using the existing function
        success, message = set_data.delete_group(group_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash('An error occurred while deleting the group: {}'.format(str(e)), 'error')
    
    return redirect(url_for('groups_list'))







# Category Management Section
@app.route('/categories', methods=["GET", "POST"])
@login_required
def manage_categories():
    """Manage user's custom categories"""
    
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'add':
            category_name = request.form.get('category_name', '').strip()
            if category_name:
                category_id = set_data.add_category(category_name, session.get('id'))
                if category_id:
                    flash('Category added successfully.', 'success')
                else:
                    flash('Failed to add category. Category name may already exist.', 'error')
            else:
                flash('Category name is required.', 'error')
        
        elif action == 'edit':
            category_id = request.form.get('category_id')
            category_name = request.form.get('category_name', '').strip()
            if category_id and category_name:
                success = set_data.update_category(category_id, category_name, session.get('id'))
                if success:
                    flash('Category updated successfully.', 'success')
                else:
                    flash('Failed to update category.', 'error')
            else:
                flash('Category ID and name are required.', 'error')
        
        elif action == 'delete':
            category_id = request.form.get('category_id')
            if category_id:
                success, message = set_data.delete_category(category_id, session.get('id'))
                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'error')
            else:
                flash('Category ID is required.', 'error')
        
        return redirect(url_for('manage_categories'))
    
    # Get user's categories with item counts
    categories = get_data.get_all_from_categories()
    
    # Add item count for each category
    cur = mysql.connection.cursor()
    for category in categories:
        cur.execute("SELECT COUNT(*) as count FROM items WHERE category_id = %s", (category['id'],))
        result = cur.fetchone()
        category['item_count'] = result['count']
    cur.close()
    
    return render_template('categories_manage.html', categories=categories)

# Admin Section
@app.context_processor
def inject_pending_requests():
    """Inject pending requests count into all templates for admin notification"""
    if session.get('loggedin') and session.get('is_admin'):
        try:
            pending_attempts = set_data.get_pending_access_attempts()
            return {'pending_requests_count': len(pending_attempts)}
        except Exception as e:
            print("Error getting pending requests count: {}".format(e))
            return {'pending_requests_count': 0}
    return {'pending_requests_count': 0}

@app.route('/admin', methods=["GET", "POST"])
@admin_required
def admin_panel():
    """Admin panel for managing users and system settings"""
    

    
    try:
        # Get all users for admin management
        users = get_data.get_all_users()
        
        # Get all groups for group management
        groups = get_data.get_all_groups()
        
        # Get pending access attempts
        pending_attempts = set_data.get_pending_access_attempts()
        
        if request.method == "POST":
            action = request.form.get('action')
            
            if action == 'toggle_admin':
                # Toggle admin status
                user_id = request.form.get('user_id')
                success = set_data.toggle_admin_status(user_id)
                if success:
                    flash('Admin status updated successfully.', 'success')
                else:
                    flash('Failed to update admin status.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'delete_user':
                # Deactivate/Activate user (only if not the current admin)
                user_id = request.form.get('user_id')
                current_user_id = session.get('id')
                
                if not user_id:
                    flash('User ID is required.', 'error')
                    return redirect(url_for('admin_panel'))
                
                if user_id != current_user_id:
                    success = set_data.toggle_user_status(user_id)
                    if success:
                        flash('User status updated successfully.', 'success')
                    else:
                        flash('Failed to update user status.', 'error')
                else:
                    flash('Cannot modify your own account status.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'approve_access':
                # Approve access for a pending user
                attempt_id = request.form.get('attempt_id')
                email = request.form.get('email')
                name = request.form.get('name')
                
                if attempt_id and email:
                    # Create a new user account for this email
                    user_id = set_data.create_user_from_admin(email, name)
                    if user_id:
                        # Mark the attempt as approved
                        set_data.update_access_attempt_status(attempt_id, 'approved')
                        flash('Access approved for {}. User account created successfully.'.format(email), 'success')
                    else:
                        flash('Failed to create user account.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'deny_access':
                # Deny access for a pending user
                attempt_id = request.form.get('attempt_id')
                email = request.form.get('email')
                
                if attempt_id:
                    success = set_data.update_access_attempt_status(attempt_id, 'denied')
                    if success:
                        flash('Access denied for {}.'.format(email), 'success')
                    else:
                        flash('Failed to deny access.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'create_group':
                # Create a new group
                group_name = request.form.get('group_name')
                group_description = request.form.get('group_description', '')
                if group_name:
                    group_id = set_data.create_group(group_name, group_description)
                    if group_id:
                        flash('Group "{}" created successfully.'.format(group_name), 'success')
                    else:
                        flash('Failed to create group.', 'error')
                else:
                    flash('Group name is required.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'update_group':
                # Update an existing group
                group_id = request.form.get('group_id')
                group_name = request.form.get('group_name')
                group_description = request.form.get('group_description', '')
                
                if group_id and group_name:
                    success = set_data.update_group(group_id, group_name, group_description)
                    if success:
                        flash('Group "{}" updated successfully.'.format(group_name), 'success')
                    else:
                        flash('Failed to update group.', 'error')
                else:
                    flash('Group ID and name are required.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'move_user_to_group':
                # Move user to a different group
                user_id = request.form.get('user_id')
                group_id = request.form.get('group_id')
                current_user_id = session.get('id')
                
                if user_id and group_id:
                    success = set_data.move_user_to_group(user_id, group_id)
                    if success:
                        # If the user is moving themselves, update their session
                        if user_id == current_user_id:
                            session['group_id'] = group_id
                            flash('Your group has been changed successfully.', 'success')
                        else:
                            flash('User moved to group successfully.', 'success')
                    else:
                        flash('Failed to move user to group.', 'error')
                else:
                    flash('User ID and Group ID are required.', 'error')
                return redirect(url_for('admin_panel'))
            
            elif action == 'delete_group':
                # Delete a group (only if it has no members)
                group_id = request.form.get('group_id')
                if group_id:
                    success, message = set_data.delete_group(group_id)
                    if success:
                        flash(message, 'success')
                    else:
                        flash(message, 'error')
                else:
                    flash('Group ID is required.', 'error')
                return redirect(url_for('admin_panel'))
        
        # Ensure users is always a list to prevent KeyError: 0
        if not users:
            users = [{'id': '1', 'username': 'Admin', 'email': 'admin@example.com', 'is_admin': 1, 'is_current_user': 'Current User'}]
        return render_template('admin.html', users=users, groups=groups, pending_attempts=pending_attempts)
    
    except Exception as e:
        # Log the error for debugging
        print("Error in admin panel: {}".format(e))
        flash('An error occurred while loading the admin panel.', 'error')
        return redirect(url_for('index'))


@app.route('/settings/ebay-listings')
@login_required
def settings_ebay_listings():
    """Settings page to search for specific eBay item financial information"""
    return render_template('settings_ebay_listings.html', 
                         listings=[], 
                         total_listings=0,
                         total_earnings=0,
                         total_fees=0,
                         total_sales=0,
                         error=None)

@app.route('/settings/ebay-listings/search', methods=['POST'])
@login_required
def search_ebay_item_settings():
    """Search for specific eBay item financial information"""
    try:
        item_id = request.form.get('item_id', '').strip()
        
        if not item_id:
            flash('Please enter an item ID to search.', 'error')
            return redirect(url_for('settings_ebay_listings'))
        
        # Get financial information for the specific item
        # First try to get OAuth token
        token_result = get_valid_ebay_token()
        
        if token_result['success']:
            # Use OAuth 2.0 token
            user_token = token_result['access_token']
        else:
            # Fallback to legacy token
            user_token = app.config.get('EBAY_USER_TOKEN')
            if not user_token or user_token == 'YOUR_EBAY_USER_TOKEN_HERE':
                flash('eBay authentication required. Please authenticate with eBay OAuth or configure a legacy token.', 'error')
                return redirect(url_for('settings_ebay_listings'))
        
        # Get detailed transaction data for the specific item
        transaction_data = get_item_transaction_details(user_token, item_id)
        
        if transaction_data['success']:
            # Get transaction data
            trans_data = transaction_data['transaction_data']
            
            # Determine the best URL to use - prefer order ID if available
            order_id = trans_data.get('order_id') or trans_data.get('orderId')
            
            if order_id:
                ebay_url = f'https://www.ebay.com/mesh/ord/details?orderid={order_id}'
                url_type = 'Order'
            else:
                ebay_url = f'https://www.ebay.com/itm/{item_id}'
                url_type = 'Item'
            
            # Create a single listing with the financial data
            listing = {
                'itemId': item_id,
                'title': f'{url_type} ID: {order_id or item_id}',
                'description': 'Financial details for eBay item',
                'condition': 'N/A',
                'quantity': 1,
                'sku': item_id,
                'end_time': 'N/A',
                'status': 'Sold',
                'ebay_url': ebay_url,
                'order_id': order_id,
                'url_type': url_type,
                **trans_data
            }
            
            
            listings = [listing]
            total_listings = 1
            total_earnings = listing.get('net_earnings', 0)
            total_fees = listing.get('total_fees', 0) or listing.get('final_value_fee', 0)
            total_sales = listing.get('final_price', 0)
            
            
            flash('Financial information retrieved for item ID: {}'.format(item_id), 'success')
        else:
            listings = []
            total_listings = 0
            total_earnings = 0
            total_fees = 0
            total_sales = 0
            flash("Error retrieving financial information: {}".format(transaction_data['error']), 'error')
        
        return render_template('settings_ebay_listings.html', 
                             listings=listings, 
                             total_listings=total_listings,
                             total_earnings=total_earnings,
                             total_fees=total_fees,
                             total_sales=total_sales,
                             searched_item_id=item_id,
                             error=transaction_data.get('error'))
    
    except Exception as e:
        print("Error in eBay item search: {}".format(e))
        flash('An error occurred while searching for the item.', 'error')
        return redirect(url_for('settings_ebay_listings'))


# Admin API endpoints
@app.route('/admin/api/group-members/<group_id>')
@admin_required
def api_group_members(group_id):
    """API endpoint to get group members"""
    try:
        members = get_data.get_group_members(group_id)
        return jsonify({
            'success': True,
            'members': members
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# JSON API endpoints for iOS app
@app.route('/api/items/search', methods=['GET'])
@login_required
def api_items_search():
    """Real-time search API for items"""
    try:
        name = request.args.get('name', '')
        sold = request.args.get('sold', '')
        
        # Handle "All Items" case (empty sold parameter)
        if sold == '':
            # Use '%' to match all sold statuses
            sold = '%'
        
        # Get search results
        items = get_data.get_list_of_items_with_name(name, sold)
        
        # Convert to JSON-serializable format
        results = []
        for item in items:
            results.append({
                'id': item['id'],
                'name': item['name'],
                'sold': item['sold'],
                'storage': item['storage'],
                'ebay_item_id': item['ebay_item_id'],
                'category_id': item['category_id'],
                'returned': item['returned'],
                'list_date': item['list_date'].strftime('%Y-%m-%d') if item['list_date'] else '',
                'gross_price': item['gross_price'],
                'shipping_fee': item['shipping_fee'],
                'sale_date': item['sale_date'].strftime('%Y-%m-%d') if item['sale_date'] else '',
                'net': item['net'],
                'group_id': item['group_id'],
                'group_name': item['group_name']
            })
        
        return jsonify({'success': True, 'items': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
@login_required
def api_categories():
    """API endpoint to get all categories"""
    try:
        categories = get_data.get_all_from_categories()
        results = []
        for category in categories:
            results.append({
                'id': category['id'],
                'type': category['type']
            })
        return jsonify({'success': True, 'categories': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/groups/search', methods=['GET'])
@login_required
def api_groups_search():
    """Real-time search API for groups"""
    try:
        name = request.args.get('name', '')
        
        # Get search results
        groups = get_data.get_all_from_group_and_items_by_name(name)
        
        # Convert to JSON-serializable format
        results = []
        for group in groups:
            results.append({
                'id': group['id'],
                'name': group['name'],
                'price': group['price'],
                'date': group['date'],
                'net': group['net'],
                'total_items': group['total_items'],
                'sold_items': group['sold_items'],
                'location_address': group.get('location_address')
            })
        
        return jsonify({'success': True, 'groups': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/groups', methods=['GET'])
@login_required
def api_get_groups():
    """Get all groups as JSON for iOS app"""
    try:
        # Get all groups using the existing function
        groups_data = get_data.get_all_from_group_and_items("%-%-%")
        
        # Convert to JSON format
        groups = []
        for group in groups_data:
            groups.append({
                'id': group['id'],
                'name': group['name'],
                'description': group.get('description', ''),
                'created_at': group.get('created_at', ''),
                'updated_at': group.get('updated_at', '')
            })
        
        return jsonify({
            'success': True,
            'groups': groups
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/categories/<category_id>/items', methods=['GET'])
@login_required
def api_get_category_items(category_id):
    """Get items for a specific category"""
    try:
        item_categories = get_data.get_list_of_items_with_categories(category_id)
        return jsonify({
            'success': True,
            'items': item_categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/groups/add', methods=['POST'])
@login_required
def api_add_group():
    """Add a new group via JSON API"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Name is required'
            }), 400
        
        name = data['name']
        description = data.get('description', '')
        
        # Use the existing group creation logic
        result = set_data.add_group(name, description)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Group added successfully',
                'group_id': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to add group'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/reports/neighborhood/detail/<neighborhood_id>')
@login_required
def neighborhood_detail(neighborhood_id):
    """Show detailed view of collections for a specific neighborhood"""
    # Get neighborhood information
    neighborhood = get_data.get_neighborhood_by_id(neighborhood_id)
    if not neighborhood:
        flash('Neighborhood not found', 'error')
        return redirect(url_for('reports_neighborhood'))
    
    # Get collections for this neighborhood
    collections = get_data.get_neighborhood_collections(neighborhood_id)
    
    # Get sales summary for this neighborhood
    sales_data = get_data.get_neighborhood_sales_data(neighborhood_id)
    
    return render_template('neighborhood_detail.html', 
                         neighborhood=neighborhood,
                         collections=collections,
                         sales_data=sales_data)

# Neighborhood Management Routes
@app.route('/settings/neighborhoods', methods=["GET", "POST"])
@login_required
def manage_neighborhoods():
    """Manage neighborhoods - create, edit, delete"""
    form = NeighborhoodForm()
    
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'create':
            # Create new neighborhood
            details = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'city': request.form.get('city', '').strip(),
                'state': request.form.get('state', '').strip()
            }
            
            success, message = set_data.create_neighborhood(details)
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
        
        elif action == 'update':
            # Update existing neighborhood
            neighborhood_id = request.form.get('neighborhood_id')
            if neighborhood_id:
                details = {
                    'name': request.form.get('name', '').strip(),
                    'description': request.form.get('description', '').strip(),
                    'city': request.form.get('city', '').strip(),
                    'state': request.form.get('state', '').strip()
                }
                
                success, message = set_data.update_neighborhood(neighborhood_id, details)
                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'error')
            else:
                flash('Neighborhood ID is required.', 'error')
        
        elif action == 'delete':
            # Delete neighborhood
            neighborhood_id = request.form.get('neighborhood_id')
            if neighborhood_id:
                success, message = set_data.delete_neighborhood(neighborhood_id)
                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'error')
            else:
                flash('Neighborhood ID is required.', 'error')
        
        return redirect(url_for('manage_neighborhoods'))
    
    # Get all neighborhoods for the current user
    neighborhoods = get_data.get_user_neighborhoods()
    
    return render_template('neighborhoods_manage.html', neighborhoods=neighborhoods, form=form)

@app.route('/settings/neighborhoods/edit/<neighborhood_id>')
@login_required
def edit_neighborhood(neighborhood_id):
    """Edit a specific neighborhood"""
    neighborhood = get_data.get_neighborhood_by_id(neighborhood_id)
    if not neighborhood:
        flash('Neighborhood not found', 'error')
        return redirect(url_for('manage_neighborhoods'))
    
    form = NeighborhoodForm()
    form.name.data = neighborhood['name']
    form.description.data = neighborhood['description']
    
    return render_template('neighborhoods_edit.html', neighborhood=neighborhood, form=form)

@app.route('/assign-neighborhood', methods=['POST'])
@login_required
def assign_neighborhood():
    """Assign a collection to a neighborhood"""
    try:
        collection_id = request.form.get('collection_id')
        neighborhood_id = request.form.get('neighborhood_id')
        
        if not collection_id:
            return jsonify({'success': False, 'message': 'Collection ID is required'}), 400
        
        # Allow empty neighborhood_id to unassign
        success, message = set_data.assign_neighborhood_to_collection(collection_id, neighborhood_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])
