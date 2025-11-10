#!/usr/bin/env python3
"""
Desktop OAuth flow using the existing redirect URIs from your OAuth client.
This should work with your current Google Cloud setup.
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv
import requests

load_dotenv()

def desktop_oauth_flow():
    """OAuth flow using desktop application method."""
    
    print("🔧 Desktop OAuth Flow for Chloros Blog MCP Server")
    print("=" * 60)
    
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"Using Client ID: {CLIENT_ID}")
    print(f"Using Client Secret: {CLIENT_SECRET[:15]}...")
    
    # Use the "out of band" redirect URI for desktop apps
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    
    # Required scopes
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Build authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"
    
    print(f"\n🌐 STEP 1: Open this URL in your browser:")
    print(f"{auth_url}")
    print(f"\n📋 Instructions:")
    print(f"1. Click the URL above (or copy/paste into browser)")
    print(f"2. Sign in with your Google account") 
    print(f"3. Grant permissions for all 3 scopes")
    print(f"4. Google will show you a CODE on the page")
    print(f"5. Copy that code and come back here")
    
    # Open browser automatically
    try:
        webbrowser.open(auth_url)
        print(f"✅ Browser opened automatically")
    except:
        print(f"❌ Could not open browser - please copy the URL manually")
    
    print(f"\n⏳ Waiting for you to complete authorization...")
    print(f"Once you have the code, come back and tell me!")
    
    return auth_url

if __name__ == "__main__":
    auth_url = desktop_oauth_flow()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Complete the authorization in your browser")
    print(f"2. Copy the authorization code Google gives you")
    print(f"3. Let me know the code and I'll exchange it for tokens")
    
    print(f"\n💡 If you get redirect_uri_mismatch error:")
    print(f"   Add this URI to your OAuth client in Google Cloud Console:")
    print(f"   urn:ietf:wg:oauth:2.0:oob")
