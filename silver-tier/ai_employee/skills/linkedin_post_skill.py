#!/usr/bin/env python3
"""
LinkedIn Post Skill - Real API Integration

Handles OAuth 2.0 authentication and posting to LinkedIn via official API.
Integrates with MCP architecture and approval workflow.
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ai_employee.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__name__)


class LinkedInPostSkill:
    """
    LinkedIn posting skill with OAuth 2.0 authentication.

    Features:
    - OAuth 2.0 authorization code flow
    - Automatic token refresh
    - Secure token storage
    - Rate limit handling
    - Error recovery
    """

    # LinkedIn API endpoints
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE = "https://api.linkedin.com/v2"

    # Required scopes
    REQUIRED_SCOPES = ["w_member_social", "r_liteprofile"]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        token_file: Optional[Path] = None,
    ):
        """
        Initialize LinkedIn Post Skill.

        Args:
            client_id: LinkedIn app client ID (from env if not provided)
            client_secret: LinkedIn app client secret (from env if not provided)
            redirect_uri: OAuth redirect URI (from env if not provided)
            token_file: Path to token storage file
        """
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv(
            "LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"
        )

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "LinkedIn credentials not configured. Set LINKEDIN_CLIENT_ID "
                "and LINKEDIN_CLIENT_SECRET environment variables."
            )

        # Token storage
        self.token_file = token_file or Path("ai_employee_vault/.linkedin_tokens.json")
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.person_urn = None

        # Load existing tokens
        self._load_tokens()

        logger.info("LinkedIn Post Skill initialized")

    def _load_tokens(self):
        """Load tokens from storage file."""
        if not self.token_file.exists():
            logger.info("No existing LinkedIn tokens found")
            return

        try:
            with open(self.token_file, "r") as f:
                data = json.load(f)

            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            self.person_urn = data.get("person_urn")

            expires_at = data.get("expires_at")
            if expires_at:
                self.token_expires_at = datetime.fromisoformat(expires_at)

            logger.info("LinkedIn tokens loaded from storage")
        except Exception as e:
            logger.error(f"Error loading LinkedIn tokens: {e}")

    def _save_tokens(self):
        """Save tokens to storage file."""
        try:
            data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "person_urn": self.person_urn,
                "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            }

            # Ensure directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)

            # Write with restricted permissions
            with open(self.token_file, "w") as f:
                json.dump(data, f, indent=2)

            # Set file permissions (owner read/write only)
            os.chmod(self.token_file, 0o600)

            logger.info("LinkedIn tokens saved to storage")
        except Exception as e:
            logger.error(f"Error saving LinkedIn tokens: {e}")

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get OAuth authorization URL for user to visit.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.REQUIRED_SCOPES),
        }

        if state:
            params["state"] = state

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{self.AUTH_URL}?{query_string}"

        logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url

    def exchange_code_for_token(self, code: str) -> bool:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")

            # Calculate expiration time
            expires_in = token_data.get("expires_in", 5184000)  # Default 60 days
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Get person URN
            self._fetch_person_urn()

            # Save tokens
            self._save_tokens()

            logger.info("Successfully exchanged code for access token")
            return True

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False

    def _fetch_person_urn(self):
        """Fetch person URN (user ID) from LinkedIn API."""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.API_BASE}/me", headers=headers)
            response.raise_for_status()

            data = response.json()
            self.person_urn = data["id"]

            logger.info(f"Fetched person URN: {self.person_urn}")
        except Exception as e:
            logger.error(f"Error fetching person URN: {e}")

    def _refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token.

        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False

        try:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)

            # Calculate expiration time
            expires_in = token_data.get("expires_in", 5184000)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Save tokens
            self._save_tokens()

            logger.info("Successfully refreshed access token")
            return True

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return False

    def _ensure_valid_token(self) -> bool:
        """
        Ensure access token is valid, refresh if needed.

        Returns:
            True if token is valid, False otherwise
        """
        if not self.access_token:
            logger.error("No access token available. Run OAuth flow first.")
            return False

        # Check if token is expired or about to expire (within 5 minutes)
        if self.token_expires_at:
            time_until_expiry = (self.token_expires_at - datetime.now()).total_seconds()
            if time_until_expiry < 300:  # 5 minutes
                logger.info("Token expired or expiring soon, refreshing...")
                return self._refresh_access_token()

        return True

    def publish(self, content: str, visibility: str = "PUBLIC") -> Tuple[bool, str]:
        """
        Post content to LinkedIn.

        Args:
            content: Post content (text)
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Ensure valid token
        if not self._ensure_valid_token():
            return False, "Authentication failed. Please run OAuth flow."

        if not self.person_urn:
            self._fetch_person_urn()
            if not self.person_urn:
                return False, "Failed to get user profile information"

        try:
            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{self.person_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
            }

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            }

            response = requests.post(
                f"{self.API_BASE}/ugcPosts",
                headers=headers,
                json=post_data,
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Retry after {retry_after} seconds")
                return False, f"Rate limited. Please wait {retry_after} seconds."

            response.raise_for_status()

            post_id = response.headers.get("X-RestLi-Id")
            logger.info(f"Successfully posted to LinkedIn. Post ID: {post_id}")

            return True, f"Successfully posted to LinkedIn. Post ID: {post_id}"

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error posting to LinkedIn: {e}"
            logger.error(error_msg)

            # Try to extract error details
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                pass

            return False, error_msg

        except Exception as e:
            error_msg = f"Error posting to LinkedIn: {e}"
            logger.error(error_msg)
            return False, error_msg

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self.access_token is not None and self._ensure_valid_token()


# CLI for OAuth flow
if __name__ == "__main__":
    import sys
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    print("LinkedIn OAuth Setup")
    print("=" * 60)

    skill = LinkedInPostSkill()

    if skill.is_authenticated():
        print("✅ Already authenticated!")
        print(f"Person URN: {skill.person_urn}")
        sys.exit(0)

    # Generate authorization URL
    auth_url = skill.get_authorization_url(state="setup")

    print("\nStep 1: Visit this URL to authorize:")
    print(auth_url)
    print("\nStep 2: After authorization, you'll be redirected to localhost.")
    print("The authorization code will be captured automatically.\n")

    # Simple HTTP server to capture callback
    auth_code = [None]  # Use list to allow modification from class method

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)

            if "code" in params:
                auth_code[0] = params["code"][0]

                # Send success response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authorization successful!</h1>")
                self.wfile.write(b"<p>You can close this window and return to the terminal.</p>")
            else:
                # Send error response
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authorization failed!</h1>")
                self.wfile.write(b"<p>No authorization code received.</p>")

        def log_message(self, format, *args):
            pass  # Suppress log messages

    # Start server
    server = HTTPServer(("localhost", 8000), CallbackHandler)
    print("Waiting for authorization callback...")

    # Handle one request
    server.handle_request()

    if auth_code[0]:
        print("\n✅ Authorization code received!")
        print("Exchanging code for access token...")

        if skill.exchange_code_for_token(auth_code[0]):
            print("✅ Successfully authenticated!")
            print(f"Person URN: {skill.person_urn}")
            print(f"Tokens saved to: {skill.token_file}")
        else:
            print("❌ Failed to exchange code for token")
            sys.exit(1)
    else:
        print("❌ No authorization code received")
        sys.exit(1)
