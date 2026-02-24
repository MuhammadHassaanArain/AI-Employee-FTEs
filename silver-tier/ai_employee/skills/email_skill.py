"""
Email Skill (Silver Tier - Enhanced)

Agent Skill for sending emails via MCP server.
Integrates with Gmail API through MCP protocol.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class EmailSkill:
    """
    Agent Skill: Send emails via MCP server.

    Silver Tier Requirement: MCP server with send_email tool.
    """

    def __init__(self, vault_path: Path, mcp_server=None):
        """
        Initialize email skill.

        Args:
            vault_path: Path to Obsidian vault
            mcp_server: MCP server instance (required for actual email sending)
        """
        self.vault_path = vault_path
        self.mcp_server = mcp_server

        if not mcp_server:
            logger.warning("EmailSkill initialized without MCP server - emails will fail")
        else:
            logger.info("Email Skill initialized (Silver Tier - Enhanced)")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Send email via MCP server.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of file paths to attach (optional)

        Returns:
            Dictionary with status and message_id
        """
        logger.info(f"EmailSkill: Sending email to {to}")

        # Validate email address
        if not self.validate_email(to):
            logger.error(f"Invalid email address: {to}")
            return {
                "status": "error",
                "error": f"Invalid email address: {to}",
            }

        # Check if MCP server is available
        if not self.mcp_server:
            logger.error("MCP server not configured")
            return {
                "status": "error",
                "error": "MCP server not configured. Cannot send email.",
            }

        # Call MCP server send_email tool
        try:
            result = self.mcp_server.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
            )

            if result.get("status") == "success":
                logger.info(f"Email sent successfully: {result.get('message_id', 'unknown')}")
            else:
                logger.error(f"Email sending failed: {result.get('error', 'unknown error')}")

            return result

        except Exception as e:
            logger.error(f"Error calling MCP server: {e}")
            return {
                "status": "error",
                "error": f"MCP server error: {str(e)}",
            }

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or "@" not in email:
            return False

        parts = email.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts
        if not local or not domain:
            return False

        if "." not in domain:
            return False

        return True

    def format_email_body(self, content: str, template: Optional[str] = None) -> str:
        """
        Format email body with optional template.

        Args:
            content: Email content
            template: Optional template name

        Returns:
            Formatted email body
        """
        if template == "professional":
            return f"""Hello,

{content}

Best regards,
AI Employee (Silver Tier)
"""
        elif template == "brief":
            return content
        else:
            # Default template
            return f"""{content}

---
Sent by AI Employee Silver Tier
"""

    def send_from_task(self, task_content: str, task_title: str = "") -> Dict[str, Any]:
        """
        Parse task content and send email.

        Args:
            task_content: Task content with email details
            task_title: Task title (used as subject if not found in content)

        Returns:
            Send result dictionary
        """
        logger.info("EmailSkill: Parsing task and sending email...")

        # Simple parsing - look for email patterns
        import re

        # Extract email address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, task_content)

        if not emails:
            logger.error("No email address found in task content")
            return {
                "status": "error",
                "error": "No email address found in task content",
            }

        to_email = emails[0]

        # Use task title as subject, or extract from content
        subject = task_title or "Message from AI Employee"

        # Use task content as body
        body = self.format_email_body(task_content, template="professional")

        # Send email
        return self.send_email(to=to_email, subject=subject, body=body)


def main():
    """CLI entry point for testing email skill."""
    from ai_employee.config import Config
    from ai_employee.mcp.mcp_server import MCPServer

    config = Config()

    # Initialize MCP server
    mcp_server = MCPServer(vault_path=config.vault_path, use_mcp_client=False)

    # Initialize email skill with MCP server
    skill = EmailSkill(vault_path=config.vault_path, mcp_server=mcp_server)

    print("=" * 60)
    print("Email Skill - Silver Tier (Enhanced)")
    print("=" * 60)

    # Test email validation
    print("\nTesting email validation:")
    print(f"  test@example.com: {skill.validate_email('test@example.com')}")
    print(f"  invalid-email: {skill.validate_email('invalid-email')}")
    print(f"  @example.com: {skill.validate_email('@example.com')}")
    print(f"  test@: {skill.validate_email('test@')}")

    # Test email formatting
    print("\nTesting email formatting:")
    content = "This is a test message."
    print(f"  Professional template:\n{skill.format_email_body(content, 'professional')}")

    print("\n" + "=" * 60)
    print("Email Skill Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
