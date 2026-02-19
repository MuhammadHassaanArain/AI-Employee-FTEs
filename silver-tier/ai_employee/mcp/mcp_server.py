"""
MCP Server (Silver Tier - Simplified)

Simple action dispatcher for external actions.
NOT full MCP protocol - just a hackathon-friendly dispatcher.

Provides tools:
- send_email: Send emails via SMTP
- post_linkedin: Simulate posting by writing to LinkedIn_Posts/
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class MCPServer:
    """
    Simple MCP Server for external actions.

    Provides tools:
    - send_email: Send emails via SMTP
    - post_linkedin: Simulate posting to LinkedIn

    Silver Tier Requirement: MCP server with external action tools.
    """

    def __init__(self, vault_path: Path, smtp_server: str = None, smtp_port: int = None):
        """
        Initialize MCP server.

        Args:
            vault_path: Path to Obsidian vault
            smtp_server: SMTP server address (default: smtp.gmail.com)
            smtp_port: SMTP port (default: 587)
        """
        self.vault_path = vault_path
        self.linkedin_posts_folder = vault_path / "LinkedIn_Posts"

        # SMTP configuration
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_email = os.getenv("SMTP_EMAIL") or os.getenv("GMAIL_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_PASSWORD")

        # Ensure LinkedIn_Posts folder exists
        self.linkedin_posts_folder.mkdir(parents=True, exist_ok=True)

        logger.info("MCP Server initialized (Silver Tier - Simplified)")

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
        MCP Tool: Send email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
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
            msg['From'] = self.smtp_email
            msg['To'] = to
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={Path(file_path).name}'
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
                    recipients.extend([addr.strip() for addr in cc.split(',')])
                if bcc:
                    recipients.extend([addr.strip() for addr in bcc.split(',')])

                server.sendmail(self.smtp_email, recipients, msg.as_string())

            # Get message ID
            message_id = msg.get('Message-ID', f"<{datetime.now().timestamp()}@mcp-server>")

            result = {
                "status": "success",
                "message_id": message_id,
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
            }

            logger.info(f"Email sent successfully: {message_id}")
            return result

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return {
                "status": "error",
                "error": "SMTP authentication failed. Check your email and password (use App Password for Gmail).",
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def post_linkedin(
        self,
        content: str,
        image_path: Optional[str] = None,
        link_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        MCP Tool: Simulate posting to LinkedIn.

        For hackathon simplicity, this writes the post to LinkedIn_Posts/ folder
        instead of actually posting to LinkedIn API.

        Args:
            content: Post content (text)
            image_path: Optional path to image to attach
            link_url: Optional URL to share

        Returns:
            Dictionary with:
            - status: "success" or "error"
            - post_id: Post ID (timestamp-based)
            - post_file: Path to saved post file
            - error: Error message (if error)
        """
        logger.info("MCP Tool: post_linkedin (simulated)")

        try:
            # Generate post ID and filename
            timestamp = datetime.now()
            post_id = timestamp.strftime("%Y%m%d-%H%M%S")
            post_filename = f"linkedin-post-{post_id}.md"
            post_path = self.linkedin_posts_folder / post_filename

            # Format post content
            post_content = f"""# LinkedIn Post

**Post ID**: {post_id}
**Created**: {timestamp.isoformat()}
**Status**: Queued for posting

---

## Content

{content}
"""

            if link_url:
                post_content += f"\n**Link**: {link_url}\n"

            if image_path:
                post_content += f"\n**Image**: {image_path}\n"

            post_content += f"""
---

## Instructions

This post has been saved to the LinkedIn queue.

To actually post to LinkedIn:
1. Copy the content above
2. Go to https://www.linkedin.com/
3. Create a new post
4. Paste the content
5. Add any images/links
6. Click "Post"

Or integrate with LinkedIn API for automated posting.
"""

            # Save post to file
            post_path.write_text(post_content, encoding="utf-8")

            result = {
                "status": "success",
                "post_id": post_id,
                "post_file": str(post_path),
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "created_at": timestamp.isoformat(),
            }

            logger.info(f"LinkedIn post saved: {post_path}")
            return result

        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {e}")
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
                "description": "Send an email via SMTP",
                "parameters": {
                    "to": {"type": "string", "required": True, "description": "Recipient email address"},
                    "subject": {"type": "string", "required": True, "description": "Email subject"},
                    "body": {"type": "string", "required": True, "description": "Email body (plain text)"},
                    "cc": {"type": "string", "required": False, "description": "CC recipients (comma-separated)"},
                    "bcc": {"type": "string", "required": False, "description": "BCC recipients (comma-separated)"},
                    "attachments": {"type": "array", "required": False, "description": "List of file paths to attach"},
                },
            },
            {
                "name": "post_linkedin",
                "description": "Post content to LinkedIn (simulated - writes to LinkedIn_Posts/)",
                "parameters": {
                    "content": {"type": "string", "required": True, "description": "Post content (text)"},
                    "image_path": {"type": "string", "required": False, "description": "Path to image to attach"},
                    "link_url": {"type": "string", "required": False, "description": "URL to share"},
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
    server = MCPServer(vault_path=config.vault_path)

    print("=" * 60)
    print("MCP Server - Silver Tier (Simplified)")
    print("=" * 60)

    # List available tools
    tools = server.list_tools()
    print(f"\nAvailable MCP tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # Test post_linkedin tool (always works - file-based)
    print("\n" + "=" * 60)
    print("Testing post_linkedin tool...")
    print("=" * 60)
    result = server.execute_tool(
        "post_linkedin",
        {
            "content": "Excited to share that I've been working on an AI Employee system! 🚀\n\nThis Silver Tier assistant can:\n- Monitor Gmail for tasks\n- Generate intelligent plans\n- Request human approval for sensitive actions\n- Execute approved tasks automatically\n\nBuilt with Python and Claude AI. #AI #Automation #Productivity",
            "link_url": "https://github.com/yourusername/ai-employee",
        },
    )
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Post ID: {result['post_id']}")
        print(f"Post file: {result['post_file']}")
        print(f"Preview: {result['content_preview']}")
    else:
        print(f"Error: {result['error']}")

    # Test send_email tool (requires SMTP credentials)
    print("\n" + "=" * 60)
    print("Testing send_email tool...")
    print("=" * 60)

    if not server.smtp_email or not server.smtp_password:
        print("SMTP credentials not configured.")
        print("To test email sending, set environment variables:")
        print("  SMTP_EMAIL=your-email@gmail.com")
        print("  SMTP_PASSWORD=your-app-password")
        print("\nSkipping email test.")
    else:
        print(f"SMTP configured: {server.smtp_email}")
        print("Note: This will send a real email!")
        print("Uncomment the code below to test:")
        print("""
        result = server.execute_tool(
            "send_email",
            {
                "to": "test@example.com",
                "subject": "Test Email from MCP Server",
                "body": "This is a test email sent from the AI Employee MCP server.\\n\\nBest regards,\\nAI Employee",
            },
        )
        print(f"Result: {result}")
        """)

    print("\n" + "=" * 60)
    print("MCP Server Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
