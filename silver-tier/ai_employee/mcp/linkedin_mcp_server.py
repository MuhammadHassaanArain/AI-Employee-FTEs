#!/usr/bin/env python3
"""
LinkedIn MCP Server

FastMCP server for LinkedIn API integration.
Provides tools for OAuth setup and posting.
"""

from fastmcp import FastMCP
from ai_employee.skills.linkedin_post_skill import LinkedInPostSkill
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP("LinkedIn")

# Initialize LinkedIn skill
linkedin_skill = None

try:
    linkedin_skill = LinkedInPostSkill()
    logger.info("LinkedIn skill initialized")
except Exception as e:
    logger.error(f"Failed to initialize LinkedIn skill: {e}")


@mcp.tool()
def linkedin_get_auth_url() -> str:
    """
    Get LinkedIn OAuth authorization URL.

    Returns:
        Authorization URL for user to visit
    """
    if not linkedin_skill:
        return "Error: LinkedIn skill not initialized. Check credentials."

    try:
        auth_url = linkedin_skill.get_authorization_url(state="mcp")
        return f"Visit this URL to authorize: {auth_url}"
    except Exception as e:
        logger.error(f"Error getting auth URL: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def linkedin_exchange_code(code: str) -> str:
    """
    Exchange authorization code for access token.

    Args:
        code: Authorization code from OAuth callback

    Returns:
        Success or error message
    """
    if not linkedin_skill:
        return "Error: LinkedIn skill not initialized. Check credentials."

    try:
        success = linkedin_skill.exchange_code_for_token(code)
        if success:
            return f"✅ Successfully authenticated! Person URN: {linkedin_skill.person_urn}"
        else:
            return "❌ Failed to exchange code for token"
    except Exception as e:
        logger.error(f"Error exchanging code: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def linkedin_check_auth() -> str:
    """
    Check if LinkedIn is authenticated.

    Returns:
        Authentication status
    """
    if not linkedin_skill:
        return "Error: LinkedIn skill not initialized. Check credentials."

    try:
        if linkedin_skill.is_authenticated():
            return f"✅ Authenticated. Person URN: {linkedin_skill.person_urn}"
        else:
            return "❌ Not authenticated. Run OAuth flow first."
    except Exception as e:
        logger.error(f"Error checking auth: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def linkedin_post(content: str, visibility: str = "PUBLIC") -> str:
    """
    Post content to LinkedIn.

    Args:
        content: Post content (text)
        visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)

    Returns:
        Success or error message with post ID
    """
    if not linkedin_skill:
        return "Error: LinkedIn skill not initialized. Check credentials."

    try:
        success, message = linkedin_skill.publish(content, visibility)
        return message
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {e}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
