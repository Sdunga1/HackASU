"""
Authentication service for OAuth integration
Supports Google and GitHub OAuth 2.0 flows
"""
import os
from typing import Optional, Dict
import httpx
from dotenv import load_dotenv

load_dotenv()

class OAuthService:
    """Service for handling OAuth authentication"""
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:3000/auth/callback")
    
    async def get_google_auth_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.google_client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def get_github_auth_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        base_url = "https://github.com/login/oauth/authorize"
        params = {
            "client_id": self.github_client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def exchange_google_code(self, code: str) -> Dict:
        """Exchange Google authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def exchange_github_code(self, code: str) -> Dict:
        """Exchange GitHub authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": self.github_client_id,
                    "client_secret": self.github_client_secret,
                    "redirect_uri": self.redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_github_user_info(self, access_token: str) -> Dict:
        """Get user information from GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()


# Global instance
oauth_service = OAuthService()

