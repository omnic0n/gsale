from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm, ButtonForm
from upload_function import *
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from urllib.parse import unquote
import random, os, math
import hashlib
import json
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import get_data, set_data
import files
import function
import config

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session functionality

# Initialize the extension
try:
    app.config.from_object("config.ProductionConfig")
except Exception as e:
    print(f"Warning: Could not load ProductionConfig, using default config: {e}")
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
    print(f"Error initializing MySQL: {e}")
    mysql = None

# Simple report caching
report_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(report_type, params):
    """Generate cache key for reports"""
    param_str = json.dumps(params, sort_keys=True)
    return f"{report_type}_{hashlib.md5(param_str.encode()).hexdigest()}"

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
                from urllib.parse import urlparse
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
        'state={}'
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
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
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
                print(f"Error recording access attempt: {e}")
            
            # Create new user account
            print(f"Creating new account for {email}")
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
        
        # Clear OAuth session data
        session.pop('oauth_state', None)
        session.pop('is_mobile_oauth', None)
        
        # Handle response based on request type
        if is_mobile_request:
            # For mobile, show success page with instructions to return to app
            # The iOS app will extract the session cookie from the response headers
            return render_template('mobile_oauth_success.html', 
                                 username=session['username'])
        else:
            # For web, redirect to home or next page
            flash('Login successful!', 'success')
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
            
    except Exception as e:
        print(f"OAuth error: {e}")
        error_msg = f'Authentication failed: {str(e)}'
        
        # Clear OAuth session data on error
        session.pop('oauth_state', None)
        session.pop('is_mobile_oauth', None)
        
        if is_mobile_request:
            return render_template('mobile_oauth_error.html', error=error_msg)
        else:
            flash(error_msg, 'error')
            return redirect(url_for('login'))

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

#Data Section
@app.route('/groups/create',methods=["POST","GET"])
@login_required
def group_add():
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        print(f"📝 Received form data: {details}")
        
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
                print(f"Error uploading image: {e}")
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
                'message': f'Missing required field: {str(e)}'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creating group: {str(e)}'
            }), 500
    return render_template('groups_add.html', form=form, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])

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
    return render_template('modify_group.html', group_id=group_id, form=form, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/items/mark_sold',methods=["POST","GET"])
@login_required
def mark_sold():
    id = request.args.get('item', type = str)
    sold = request.args.get('sold', type = str)
    set_data.set_mark_sold(id, sold)    
    return redirect(url_for('describe_item',item=id))

@app.route('/items/bought',methods=["POST","GET"])
@login_required
def bought_items():
    group_id = request.args.get('group', type = str)
    
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()

    form = PurchaseForm()

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
        print(details)
        group_data = get_data.get_all_from_group(details['group'])
        if not group_data:
            flash('Group not found or access denied.', 'error')
            return redirect(url_for('index'))
        set_data.set_bought_items(details)
        return redirect(url_for('group_detail',group_id=group_data['id']))
    return render_template('items_purchased.html', form=form)

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
            'message': f'Error updating item: {str(e)}'
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
    item_id = request.args.get('item', type = str)
    items = get_data.get_all_items_not_sold()

    form = SaleForm()
    form.id.choices = [(item['id'], item['name']) for item in items]
    form.id.data = item_id

    if request.method == "POST":
        details = request.form
        set_data.set_mark_sold(details['id'], 1)
        set_data.set_sale_data(details)
        return redirect(url_for('describe_item',item=details['id']))
    return render_template('items_sold.html', form=form)

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
                modify_url += f'&return_to={return_to}'
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
                            return_to=return_to)



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
    
    return render_template('groups_list_detail.html', 
                            group_id=group_id,
                            items=items,
                            total_items=total_items,
                            total_sold_items=total_sold_items,
                            sold_price=sold_price,
                            form=form,
                            quicksell=quicksell,
                            groups=groups,
                            categories=categories)

@app.route('/groups/remove',methods=["POST","GET"])
@login_required
def group_remove():
    id = request.args.get('id', type = str)
    set_data.remove_group_data(id)
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
            print(f"Error getting pending requests count: {e}")
            return {'pending_requests_count': 0}
    return {'pending_requests_count': 0}

@app.route('/admin', methods=["GET", "POST"])
@admin_required
def admin_panel():
    """Admin panel for managing users and system settings"""
    

    
    try:
        # Get all users for admin management
        users = get_data.get_all_users()
        
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
                        flash(f'Access approved for {email}. User account created successfully.', 'success')
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
                        flash(f'Access denied for {email}.', 'success')
                    else:
                        flash('Failed to deny access.', 'error')
                return redirect(url_for('admin_panel'))
        
        # Ensure users is always a list to prevent KeyError: 0
        if not users:
            users = [{'id': '1', 'username': 'Admin', 'email': 'admin@example.com', 'is_admin': 1, 'is_current_user': 'Current User'}]
        return render_template('admin.html', users=users, pending_attempts=pending_attempts)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error in admin panel: {e}")
        flash('An error occurred while loading the admin panel.', 'error')
        return redirect(url_for('index'))

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
                'net': item['net'],
                'group_id': item['group_id'],
                'group_name': item['group_name']
            })
        
        return jsonify({'success': True, 'items': results})
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
def api_groups():
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


if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])
