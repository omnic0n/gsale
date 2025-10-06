#!/usr/bin/env python3

import requests
import json

def test_ebay_token():
    """
    Test your eBay token with different API endpoints
    """
    # Replace this with your actual eBay user token
    user_token = "YOUR_EBAY_USER_TOKEN_HERE"
    
    if user_token == "YOUR_EBAY_USER_TOKEN_HERE":
        print("❌ Please update the user_token variable with your actual eBay token")
        return
    
    print("🔍 Testing eBay API token...")
    print("Token (first 20 chars):", user_token[:20] + "...")
    
    # Test different endpoints
    endpoints = [
        {
            'name': 'Inventory API',
            'url': 'https://api.ebay.com/sell/inventory/v1/inventory_item',
            'headers': {
                'Authorization': f'Bearer {user_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
            },
            'params': {'limit': 10}
        },
        {
            'name': 'Browse API',
            'url': 'https://api.ebay.com/buy/browse/v1/item_summary/search',
            'headers': {
                'Authorization': f'Bearer {user_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
            },
            'params': {'q': '*', 'limit': 10}
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing {endpoint['name']}...")
        try:
            response = requests.get(endpoint['url'], headers=endpoint['headers'], params=endpoint['params'])
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
            elif response.status_code == 403:
                print("❌ Access Denied - Check token permissions")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {response.text}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n💡 Troubleshooting Tips:")
    print("1. Make sure your token has 'selling.read' and 'selling.write' scopes")
    print("2. Check if your token is expired")
    print("3. Verify you're using the correct token format (Bearer token)")
    print("4. Ensure your eBay developer account is approved for production")

if __name__ == "__main__":
    test_ebay_token()
