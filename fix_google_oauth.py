#!/usr/bin/env python3
"""
Script to fix Google OAuth credentials for the Chloros Blog MCP Server.
This will help you generate new OAuth tokens.
"""

import os
import json
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_google_oauth():
    """Generate new Google OAuth credentials."""
    
    print("🔧 Google OAuth Credential Fix Tool")
    print("=" * 50)
    
    # OAuth 2.0 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents', 
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Client configuration
    client_config = {
        "web": {
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/callback"]
        }
    }
    
    print(f"Client ID: {client_config['web']['client_id'][:20]}...")
    print(f"Client Secret: {client_config['web']['client_secret'][:10]}...")
    
    try:
        # Create the flow
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='http://localhost:8080/callback'
        )
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        print(f"\n🌐 Please visit this URL to authorize the application:")
        print(f"{auth_url}")
        
        print(f"\n📋 After authorization, you'll be redirected to a localhost URL.")
        print(f"Copy the ENTIRE redirect URL and paste it here:")
        
        # Get the authorization response
        authorization_response = input("Redirect URL: ").strip()
        
        # Exchange the authorization code for tokens
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        
        print(f"\n✅ SUCCESS! New credentials generated:")
        print(f"Access Token: {credentials.token[:20]}...")
        print(f"Refresh Token: {credentials.refresh_token[:20]}...")
        print(f"Expires: {credentials.expiry}")
        
        # Test the credentials
        print(f"\n🧪 Testing new credentials...")
        credentials.refresh(Request())
        print(f"✅ Credentials refresh test passed!")
        
        # Save to .env file
        print(f"\n💾 Update your .env file with this refresh token:")
        print(f"GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
        
        return credentials.refresh_token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    refresh_token = fix_google_oauth()
    if refresh_token:
        print(f"\n🎉 OAuth fix complete!")
        print(f"Don't forget to update your .env file!")
    else:
        print(f"\n❌ OAuth fix failed. Try the Google OAuth Playground method instead.")
