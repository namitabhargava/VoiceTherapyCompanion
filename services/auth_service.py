import os
import streamlit as st
import requests
from datetime import datetime, timedelta
import json
from utils.security import SecurityUtils

class AuthService:
    def __init__(self):
        self.security = SecurityUtils()
        self.zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        self.zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.teams_client_id = os.getenv("TEAMS_CLIENT_ID")
        self.teams_client_secret = os.getenv("TEAMS_CLIENT_SECRET")
        
    def authenticate_zoom(self):
        """Authenticate with Zoom OAuth"""
        try:
            if not self.zoom_client_id or not self.zoom_client_secret:
                st.error("Zoom OAuth credentials not configured")
                return False
                
            # Check if already authenticated
            if self._is_token_valid('zoom'):
                return True
                
            # OAuth flow
            auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={self.zoom_client_id}&redirect_uri=https://localhost:5000/oauth/zoom"
            
            st.info("Please complete OAuth authentication in your browser")
            st.markdown(f"[Authenticate with Zoom]({auth_url})")
            
            # In a real implementation, this would handle the OAuth callback
            # For now, we'll simulate successful authentication
            self._store_token('zoom', self._generate_mock_token())
            
            return True
            
        except Exception as e:
            st.error(f"Zoom authentication failed: {str(e)}")
            return False
    
    def authenticate_google(self):
        """Authenticate with Google OAuth"""
        try:
            if not self.google_client_id or not self.google_client_secret:
                st.error("Google OAuth credentials not configured")
                return False
                
            if self._is_token_valid('google'):
                return True
                
            # OAuth flow for Google
            auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={self.google_client_id}&redirect_uri=https://localhost:5000/oauth/google&scope=https://www.googleapis.com/auth/drive.readonly"
            
            st.info("Please complete OAuth authentication in your browser")
            st.markdown(f"[Authenticate with Google]({auth_url})")
            
            self._store_token('google', self._generate_mock_token())
            
            return True
            
        except Exception as e:
            st.error(f"Google authentication failed: {str(e)}")
            return False
    
    def authenticate_teams(self):
        """Authenticate with Microsoft Teams"""
        try:
            if not self.teams_client_id or not self.teams_client_secret:
                st.error("Teams OAuth credentials not configured")
                return False
                
            if self._is_token_valid('teams'):
                return True
                
            # OAuth flow for Teams
            auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?response_type=code&client_id={self.teams_client_id}&redirect_uri=https://localhost:5000/oauth/teams&scope=https://graph.microsoft.com/Files.Read"
            
            st.info("Please complete OAuth authentication in your browser")
            st.markdown(f"[Authenticate with Teams]({auth_url})")
            
            self._store_token('teams', self._generate_mock_token())
            
            return True
            
        except Exception as e:
            st.error(f"Teams authentication failed: {str(e)}")
            return False
    
    def _is_token_valid(self, platform):
        """Check if stored token is valid"""
        try:
            tokens = self._load_tokens()
            if platform not in tokens:
                return False
                
            token_data = tokens[platform]
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            
            return datetime.now() < expires_at
            
        except Exception:
            return False
    
    def _store_token(self, platform, token_data):
        """Store OAuth token securely"""
        try:
            tokens = self._load_tokens()
            tokens[platform] = token_data
            
            # Encrypt and store
            encrypted_data = self.security.encrypt_data(json.dumps(tokens))
            
            with open('tokens.enc', 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            st.error(f"Failed to store token: {str(e)}")
    
    def _load_tokens(self):
        """Load stored tokens"""
        try:
            if not os.path.exists('tokens.enc'):
                return {}
                
            with open('tokens.enc', 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.security.decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
            
        except Exception:
            return {}
    
    def _generate_mock_token(self):
        """Generate mock token for development"""
        return {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    def get_token(self, platform):
        """Get valid token for platform"""
        if self._is_token_valid(platform):
            tokens = self._load_tokens()
            return tokens[platform]['access_token']
        return None
