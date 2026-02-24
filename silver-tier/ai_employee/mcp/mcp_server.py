"""
MCP Server (Silver Tier - Enhanced)

Orchestrator that integrates multiple action execution methods:
1. FastMCP Gmail Server (via MCPClient) - for Gmail API operations
2. SMTP fallback - for direct email sending
3. LinkedIn simulation - file-based posting

This class acts as a unified interface for the reasoning loop.
"""

import asyncio
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from ai_employee.utils.logger import get_logger
from ai_employee.mcp.mcp_client import MCPClient

logger = get_logger(__name__)


class MCPServer:
    """
    Enhanced MCP Server for external actions.

    Provides unified interface for:
    - send_email: Gmail API (via FastMCP) or SMTP fallback
    - post_linkedin: File-based simulation

    Silver Tier Requirement: MCP integration with approval workflow.
    """

    def __init__(
        self,
        vault_path: Path,
        mcp_server_url: str = "http://localhost:8000/mcp",
        use_mcp_client: bool = True,
    ):
        """
        Initialize MCP server.

        Args:
            vault_path: Path to Obsidian vault
            mcp_server_url: URL of FastMCP Gmail server
            use_mcp_client: Whether to use MCP client (True) or SMTP fallback (False)
        """
        self.vault_path = vault_path
        self.linkedin_posts_folder = vault_path / "LinkedIn_Posts"
        self.mcp_server_url = mcp_server_url
        self.use_mcp_client = use_mcp_client

        # SMTP fallback configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_email = os.getenv("SMTP_EMAIL") or os.getenv("GMAIL_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_PASSWORD")

        # Ensure LinkedIn_Posts folder exists
        self.linkedin_posts_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"MCP Server initialized (Silver Tier - Enhanced)")
        logger.info(f"  MCP Client: {'Enabled' if use_mcp_client else 'Disabled (SMTP fallback)'}")
        logger.info(f"  MCP URL: {mcp_server_url}")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        MCP Tool: Send email via FastMCP Gmail server or SMTP fallback.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional, comma-separated)
            bcc: BCC recipients (optional, comma-separated)
            attachments: List of file paths to attach (optional)

        Returns:
            Dictionary with:
            - status: "success" or "error"
            - message_id: Email message ID (if success)
            - error: Error message (if error)
        """
        logger.info(f"MCP Tool: send_email to {to}")

        if self.use_mcp_client:
            # Try FastMCP Gmail server first
            try:
                result = asyncio.run(self._send_email_via_mcp(to, subject, body))
                logger.info(f"Email sent via MCP: {result.get('message_id', 'unknown')}")
                return result
            except Exception as e:
                logger.warning(f"MCP client failed: {e}, falling back to SMTP")
                # Fall through to SMTP fallback

        # SMTP fallback
        return self._send_email_via_smtp(to, subject, body, cc, bcc, attachments)

    async def _send_email_via_mcp(
        self, to: str, subject: str, body: str
    ) -> Dict[str, Any]:
        """
        Send email via FastMCP Gmail server.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            Result dictionary from MCP server
        """
        logger.info(f"Connecting to MCP server: {self.mcp_server_url}")

        async with MCPClient(self.mcp_server_url) as client:
            # Call gmail_send_email tool
            result = await client.tool_call(
                "gmail_send_email",
                {"to": to, "subject": subject, "body": body},
            )

            # Parse MCP response
            if result and len(result) > 0:
                # MCP returns list of content blocks
                content = result[0]
                if hasattr(content, "text"):
                    # Parse JSON response
                    import json
                    response = json.loads(content.text)
                    return response
                else:
                    return {"status": "success", "message_id": str(content)}

            return {"status": "error", "error": "Empty response from MCP server"}

    def _send_email_via_smtp(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send email via SMTP (fallback method).

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            attachments: File attachments

        Returns:
            Result dictionary
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders

        logger.info(f"Sending email via SMTP fallback to {to}")

        # Check credentials
        if not self.smtp_email or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return {
                "status": "error",
                "error": "SMTP credentials not configured. Set SMTP_EMAIL and SMTP_PASSWORD environment variables.",
            }

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_email
            msg["To"] = to
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = cc
            if bcc:
                msg["Bcc"] = bcc

            # Attach body
            msg.attach(MIMEText(body, "plain"))

            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename={Path(file_path).name}",
                            )
                            msg.attach(part)
                    except Exception as e:
                        logger.warning(f"Failed to attach file {file_path}: {e}")

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)

                # Build recipient list
                recipients = [to]
                if cc:
                    recipients.extend([addr.strip() for addr in cc.split(",")])
                if bcc:
                    recipients.extend([addr.strip() for addr in bcc.split(",")])

                server.sendmail(self.smtp_email, recipients, msg.as_string())

            # Get message ID
            message_id = msg.get(
                "Message-ID", f"<{datetime.now().timestamp()}@smtp-fallback>"
            )

            result = {
                "status": "success",
                "message_id": message_id,
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "method": "smtp",
            }

            logger.info(f"Email sent via SMTP: {message_id}")
            return result

        except Exception as e:
            logger.error(f"Error sending email via SMTP: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def post_linkedin(
        self,
        content: str,
        visibility: str = "PUBLIC",
    ) -> Dict[str, Any]:
        """
        MCP Tool: Post to LinkedIn via real API.

        Uses linkedin_post_skill.py for OAuth 2.0 authentication
        and actual LinkedIn API v2 posting.

        Args:
            content: Post content (text)
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)

        Returns:
            Dictionary with:
            - status: "success" or "error"
            - post_id: LinkedIn post ID from API
            - message: Success or error message
        """
        logger.info("MCP Tool: post_linkedin (REAL API)")

        try:
            # Import LinkedIn skill
            from ai_employee.skills.linkedin_post_skill import LinkedInPostSkill

            # Initialize skill
            linkedin_skill = LinkedInPostSkill()

            # Check authentication
            if not linkedin_skill.is_authenticated():
                logger.error("LinkedIn not authenticated")
                return {
                    "status": "error",
                    "error": "LinkedIn not authenticated. Run OAuth setup first: python -m ai_employee.skills.linkedin_post_skill",
                }

            # Post to LinkedIn
            success, message = linkedin_skill.publish(content, visibility)

            if success:
                # Extract post ID from message
                post_id = None
                if "Post ID:" in message:
                    post_id = message.split("Post ID:")[-1].strip()

                logger.info(f"LinkedIn post successful: {post_id}")
                return {
                    "status": "success",
                    "post_id": post_id,
                    "message": message,
                    "content_preview": content[:100] + "..." if len(content) > 100 else content,
                    "posted_at": datetime.now().isoformat(),
                }
            else:
                logger.error(f"LinkedIn post failed: {message}")
                return {
                    "status": "error",
                    "error": message,
                }

        except ImportError as e:
            logger.error(f"LinkedIn skill not available: {e}")
            return {
                "status": "error",
                "error": f"LinkedIn skill not available: {e}",
            }
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available MCP tools.

        Returns:
            List of tool definitions
        """
        tools = [
            {
                "name": "send_email",
                "description": "Send an email via Gmail API (MCP) or SMTP fallback",
                "parameters": {
                    "to": {
                        "type": "string",
                        "required": True,
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "required": True,
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "required": True,
                        "description": "Email body (plain text)",
                    },
                    "cc": {
                        "type": "string",
                        "required": False,
                        "description": "CC recipients (comma-separated)",
                    },
                    "bcc": {
                        "type": "string",
                        "required": False,
                        "description": "BCC recipients (comma-separated)",
                    },
                    "attachments": {
                        "type": "array",
                        "required": False,
                        "description": "List of file paths to attach",
                    },
                },
            },
            {
                "name": "post_linkedin",
                "description": "Post content to LinkedIn via real API (OAuth 2.0)",
                "parameters": {
                    "content": {
                        "type": "string",
                        "required": True,
                        "description": "Post content (text)",
                    },
                    "visibility": {
                        "type": "string",
                        "required": False,
                        "description": "Post visibility: PUBLIC, CONNECTIONS, or LOGGED_IN (default: PUBLIC)",
                    },
                },
            },
        ]

        return tools

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool by name.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        logger.info(f"Executing MCP tool: {tool_name}")

        if tool_name == "send_email":
            return self.send_email(**parameters)
        elif tool_name == "post_linkedin":
            return self.post_linkedin(**parameters)
        else:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool_name}",
            }


def main():
    """CLI entry point for testing MCP server."""
    from ai_employee.config import Config

    config = Config()
    server = MCPServer(vault_path=config.vault_path, use_mcp_client=False)

    print("=" * 60)
    print("MCP Server - Silver Tier (Enhanced)")
    print("=" * 60)

    # List available tools
    tools = server.list_tools()
    print(f"\nAvailable MCP tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # Test post_linkedin tool
    print("\n" + "=" * 60)
    print("Testing post_linkedin tool...")
    print("=" * 60)
    result = server.execute_tool(
        "post_linkedin",
        {
            "content": "Excited to share my AI Employee Silver Tier system! 🚀\n\nFeatures:\n- Gmail monitoring\n- Intelligent planning\n- Human approval workflow\n- MCP integration\n\n#AI #Automation",
        },
    )
    print(f"Status: {result['status']}")
    if result["status"] == "success":
        print(f"Post ID: {result['post_id']}")
        print(f"Post file: {result['post_file']}")

    print("\n" + "=" * 60)
    print("MCP Server Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
