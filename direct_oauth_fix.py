#!/usr/bin/env python3
"""
Direct OAuth flow for Chloros Blog MCP Server.
This bypasses Google OAuth Playground to avoid redirect issues.
"""

import os
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from dotenv import load_dotenv
import requests

load_dotenv()

def direct_oauth_flow():
    """Direct OAuth 2.0 flow without using OAuth Playground."""
    
    print("🔧 Direct Google OAuth Fix for Chloros Blog MCP Server")
    print("=" * 60)
    
    # Your OAuth credentials
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"Using Client ID: {CLIENT_ID[:30]}...")
    print(f"Using Client Secret: {CLIENT_SECRET[:15]}...")
    
    # OAuth 2.0 endpoints
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    # Required scopes
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents", 
        "https://www.googleapis.com/auth/drive"
    ]
    
    # We'll use a special redirect URI that Google allows for desktop apps
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    
    # Step 1: Build authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'  # Force consent to get refresh token
    }
    
    auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
    
    print(f"\n🌐 STEP 1: Authorization")
    print(f"I will open this URL in your browser:")
    print(f"{auth_url}")
    print(f"\nAfter authorization, Google will show you an AUTHORIZATION CODE.")
    print(f"Copy that code and paste it here.")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
        print(f"✅ Browser opened automatically")
    except:
        print(f"❌ Could not open browser automatically")
        print(f"Please manually copy and paste this URL into your browser:")
        print(f"{auth_url}")
    
    # Get authorization code from user
    print(f"\n📋 STEP 2: Get Authorization Code")
    auth_code = input("Paste the authorization code here: ").strip()
    
    if not auth_code:
        print(f"❌ No authorization code provided")
        return None
    
    print(f"✅ Authorization code received: {auth_code[:20]}...")
    
    # Step 3: Exchange code for tokens
    print(f"\n🔄 STEP 3: Exchange code for tokens...")
    
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(TOKEN_URL, data=token_data)
        response.raise_for_status()
        
        tokens = response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        if not refresh_token:
            print(f"❌ No refresh token received. Make sure you clicked 'consent' during authorization.")
            return None
        
        print(f"✅ SUCCESS! Tokens received:")
        print(f"   Access Token: {access_token[:30]}...")
        print(f"   Refresh Token: {refresh_token[:30]}...")
        
        # Test the tokens
        print(f"\n🧪 STEP 4: Testing tokens...")
        test_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/tokeninfo',
            params={'access_token': access_token}
        )
        
        if test_response.status_code == 200:
            token_info = test_response.json()
            print(f"✅ Token test passed!")
            print(f"   Scopes: {token_info.get('scope', 'Unknown')}")
            print(f"   Expires in: {token_info.get('expires_in', 'Unknown')} seconds")
        else:
            print(f"⚠️ Token test failed: {test_response.status_code}")
        
        # Show .env update
        print(f"\n💾 STEP 5: Update your .env file")
        print(f"Replace these lines in your .env file:")
        print(f"")
        print(f"GOOGLE_CLIENT_ID={CLIENT_ID}")
        print(f"GOOGLE_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print(f"")
        
        return refresh_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Token exchange failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Direct OAuth Flow...")
    refresh_token = direct_oauth_flow()
    
    if refresh_token:
        print(f"\n🎉 SUCCESS! OAuth setup complete!")
        print(f"Your MCP server will work once you update the .env file.")
    else:
        print(f"\n❌ OAuth setup failed.")
        print(f"Please check your Client ID and Secret, then try again.")
