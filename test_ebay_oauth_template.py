#!/usr/bin/env python3
"""
eBay OAuth 2.0 Configuration Test Script Template
This is a template version without sensitive credentials.
Copy this file and add your actual credentials for testing.
"""

import requests
import base64
import json
from urllib.parse import urlencode
import sys

def test_ebay_oauth_config():
    """Test eBay OAuth 2.0 configuration"""
    
    print("Testing eBay OAuth 2.0 Configuration")
    print("=" * 50)
    
    # Configuration values - REPLACE WITH YOUR ACTUAL VALUES
    CLIENT_ID = 'YOUR_EBAY_CLIENT_ID_HERE'
    CLIENT_SECRET = 'YOUR_EBAY_CLIENT_SECRET_HERE'
    REDIRECT_URI = 'https://yourdomain.com/ebay-callback'
    SANDBOX_MODE = False
    
    print(f"Client ID: {CLIENT_ID}")
    print(f"Client Secret: {CLIENT_SECRET[:20]}..." if len(CLIENT_SECRET) > 20 else "Not configured")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Sandbox Mode: {SANDBOX_MODE}")
    print()
    
    # Test 1: Validate Client Secret Format
    print("Test 1: Validating Client Secret Format")
    print("-" * 40)
    
    if CLIENT_SECRET == 'YOUR_EBAY_CLIENT_SECRET_HERE':
        print("ERROR: Client Secret not configured!")
        print("   Please replace 'YOUR_EBAY_CLIENT_SECRET_HERE' with your actual Client Secret.")
        print()
        return False
    elif CLIENT_SECRET.startswith('v^'):
        print("ERROR: Client Secret appears to be a legacy token format!")
        print("   OAuth 2.0 Client Secret should be a simple string, not a legacy token.")
        print("   Please check your eBay Developer Portal for the correct Client Secret.")
        print()
        return False
    else:
        print("SUCCESS: Client Secret format looks correct (not legacy token)")
    
    # Test 2: Generate Authorization URL
    print("\nTest 2: Generating Authorization URL")
    print("-" * 40)
    
    try:
        if SANDBOX_MODE:
            auth_url = 'https://auth.sandbox.ebay.com/oauth2/authorize'
        else:
            auth_url = 'https://auth.ebay.com/oauth2/authorize'
        
        auth_params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': 'https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment',
            'state': 'test_state_123'
        }
        
        param_string = urlencode(auth_params)
        full_auth_url = f"{auth_url}?{param_string}"
        
        print(f"SUCCESS: Authorization URL generated successfully")
        print(f"   URL: {full_auth_url[:100]}...")
        print(f"   Length: {len(full_auth_url)} characters")
        
    except Exception as e:
        print(f"ERROR: generating authorization URL: {e}")
        return False
    
    # Test 3: Test Basic Auth Header Generation
    print("\nTest 3: Testing Basic Auth Header Generation")
    print("-" * 40)
    
    try:
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        basic_auth_header = f"Basic {encoded_credentials}"
        
        print(f"SUCCESS: Basic Auth header generated successfully")
        print(f"   Header: {basic_auth_header[:50]}...")
        
    except Exception as e:
        print(f"ERROR: generating Basic Auth header: {e}")
        return False
    
    # Test 4: Test Token Endpoint Connectivity
    print("\nTest 4: Testing Token Endpoint Connectivity")
    print("-" * 40)
    
    try:
        if SANDBOX_MODE:
            token_url = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
        else:
            token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        
        # Test with invalid credentials to check endpoint connectivity
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Basic {base64.b64encode('invalid:invalid'.encode()).decode()}"
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'redirect_uri': REDIRECT_URI
        }
        
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        
        print(f"SUCCESS: Token endpoint is reachable")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("   (401 Unauthorized is expected with invalid credentials)")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: connecting to token endpoint: {e}")
        return False
    except Exception as e:
        print(f"ERROR: testing token endpoint: {e}")
        return False
    
    # Test 5: Validate Configuration
    print("\nTest 5: Configuration Validation")
    print("-" * 40)
    
    issues = []
    
    if not CLIENT_ID or CLIENT_ID == 'YOUR_EBAY_CLIENT_ID_HERE':
        issues.append("Client ID is not configured")
    
    if not CLIENT_SECRET or CLIENT_SECRET == 'YOUR_EBAY_CLIENT_SECRET_HERE':
        issues.append("Client Secret is not configured")
    
    if not REDIRECT_URI or REDIRECT_URI == 'https://yourdomain.com/ebay-callback':
        issues.append("Redirect URI is not configured")
    
    if CLIENT_ID and not CLIENT_ID.startswith(('TheFrisc-', 'YourApp-')):
        issues.append("Client ID format may be incorrect")
    
    if issues:
        print("Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("SUCCESS: Configuration appears to be valid")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if CLIENT_SECRET.startswith('v^'):
        print("CRITICAL ISSUE: Client Secret is in legacy token format!")
        print("   You need to get the OAuth 2.0 Client Secret from eBay Developer Portal.")
        print("   The current value appears to be a legacy token, not an OAuth secret.")
        print()
        print("NEXT STEPS:")
        print("   1. Go to https://developer.ebay.com/my/keys")
        print("   2. Find your application")
        print("   3. Look for 'Client Secret' (not 'Cert ID' or legacy token)")
        print("   4. Copy the Client Secret and update this script")
        print("   5. The Client Secret should be a simple string, not starting with 'v^'")
        return False
    else:
        print("SUCCESS: All tests passed! Your OAuth configuration looks good.")
        print()
        print("NEXT STEPS:")
        print("   1. Start your Flask application")
        print("   2. Navigate to the admin panel")
        print("   3. Go to 'eBay Item Financial Search'")
        print("   4. Click 'Authenticate with eBay' to test the OAuth flow")
        return True

if __name__ == "__main__":
    print("WARNING: This is a template file!")
    print("Please copy this file and add your actual credentials before running.")
    print("Never commit files with real credentials to version control!")
    print()
    
    # Uncomment the line below after adding your credentials
    # success = test_ebay_oauth_config()
    # sys.exit(0 if success else 1)
