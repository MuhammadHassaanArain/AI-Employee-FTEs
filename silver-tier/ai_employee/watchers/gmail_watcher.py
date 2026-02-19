"""
Gmail Watcher (Silver Tier - IMAP Implementation)

Monitors Gmail inbox for new emails and converts them to tasks.
Uses IMAP for simple polling without OAuth complexity.
"""

import imaplib
import email
from email.header import decode_header
from email.message import Message
from pathlib import Path
from typing import List, Dict, Optional
import os
import re
from datetime import datetime
from ai_employee.watchers.task_creator import TaskCreator
from ai_employee.models.task import Task
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class GmailWatcher:
    """
    Watches Gmail inbox for new emails and creates tasks.

    Silver Tier Requirement: Second watcher (in addition to file watcher)

    Uses IMAP for simple email polling without OAuth complexity.
    """

    def __init__(self, vault_path: Path, email_address: str = None, password: str = None):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to Obsidian vault
            email_address: Gmail address (or load from env)
            password: Gmail app password (or load from env)
        """
        self.vault_path = vault_path
        self.task_creator = TaskCreator(vault_path)

        # Load credentials from environment or parameters
        self.email_address = email_address or os.getenv("GMAIL_EMAIL")
        self.password = password or os.getenv("GMAIL_PASSWORD")

        # IMAP settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

        logger.info("Gmail Watcher initialized (Silver Tier - IMAP)")

    def connect(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Connect to Gmail IMAP server.

        Returns:
            IMAP connection object or None if failed
        """
        if not self.email_address or not self.password:
            logger.error("Gmail credentials not configured. Set GMAIL_EMAIL and GMAIL_PASSWORD environment variables.")
            return None

        try:
            logger.info(f"Connecting to Gmail IMAP server: {self.imap_server}")
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            logger.info("Successfully connected to Gmail")
            return mail
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed: {e}")
            logger.error("Tip: Use Gmail App Password, not regular password")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return None

    def decode_mime_header(self, header_value: str) -> str:
        """
        Decode MIME encoded email header.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(encoding or "utf-8", errors="ignore")
                except:
                    decoded_string += part.decode("utf-8", errors="ignore")
            else:
                decoded_string += part

        return decoded_string

    def extract_email_body(self, msg: Message) -> str:
        """
        Extract email body from message.

        Args:
            msg: Email message object

        Returns:
            Email body as plain text
        """
        body = ""

        if msg.is_multipart():
            # Handle multipart messages
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Get plain text or HTML
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break  # Prefer plain text
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        html_body = part.get_payload(decode=True).decode(errors="ignore")
                        # Simple HTML to text conversion
                        body = self.html_to_text(html_body)
                    except:
                        pass
        else:
            # Handle simple messages
            try:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            except:
                body = str(msg.get_payload())

        return body.strip()

    def html_to_text(self, html: str) -> str:
        """
        Simple HTML to text conversion.

        Args:
            html: HTML content

        Returns:
            Plain text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def parse_email(self, email_id: bytes, msg_data: bytes) -> Optional[Dict]:
        """
        Parse email message into structured data.

        Args:
            email_id: Email ID from IMAP
            msg_data: Raw email message data

        Returns:
            Dictionary with email details or None if parsing failed
        """
        try:
            # Parse email message
            msg = email.message_from_bytes(msg_data)

            # Extract headers
            subject = self.decode_mime_header(msg.get("Subject", "No Subject"))
            from_header = self.decode_mime_header(msg.get("From", "Unknown"))
            date_header = msg.get("Date", "")

            # Extract email address from "Name <email@example.com>" format
            from_match = re.search(r'<(.+?)>', from_header)
            from_email = from_match.group(1) if from_match else from_header

            # Extract body
            body = self.extract_email_body(msg)

            # Parse date
            try:
                date_tuple = email.utils.parsedate_to_datetime(date_header)
                date_iso = date_tuple.isoformat()
            except:
                date_iso = datetime.utcnow().isoformat() + "Z"

            return {
                "id": email_id.decode(),
                "subject": subject,
                "from": from_header,
                "from_email": from_email,
                "date": date_iso,
                "body": body,
            }

        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return None

    def fetch_unread_emails(self) -> List[Dict]:
        """
        Fetch unread emails from Gmail inbox.

        Returns:
            List of email dictionaries
        """
        mail = self.connect()
        if not mail:
            return []

        emails = []

        try:
            # Select inbox
            mail.select("INBOX")

            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")

            if status != "OK":
                logger.warning("No unread emails found")
                return []

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")

            # Fetch each email
            for email_id in email_ids:
                try:
                    # Fetch email data
                    status, msg_data = mail.fetch(email_id, "(RFC822)")

                    if status != "OK":
                        logger.warning(f"Failed to fetch email {email_id}")
                        continue

                    # Parse email
                    email_dict = self.parse_email(email_id, msg_data[0][1])

                    if email_dict:
                        emails.append(email_dict)
                        logger.info(f"Parsed email: {email_dict['subject']}")

                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")

        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

        return emails

    def create_task_from_email(self, email_dict: Dict) -> Optional[str]:
        """
        Convert email to task in Needs_Action folder.

        Args:
            email_dict: Email dictionary with id, subject, from, body, date

        Returns:
            Task ID or None if failed
        """
        try:
            # Format task content
            task_content = f"""**From**: {email_dict['from']}
**Date**: {email_dict['date']}
**Subject**: {email_dict['subject']}

---

{email_dict['body']}
"""

            # Create task with source="gmail"
            task = Task(
                title=email_dict['subject'],
                content=task_content,
                source="gmail",
                source_path=f"gmail:{email_dict['from_email']}",
                original_filename=f"email-{email_dict['id']}.eml",
                source_metadata={
                    "email_id": email_dict['id'],
                    "from": email_dict['from'],
                    "from_email": email_dict['from_email'],
                    "date": email_dict['date'],
                },
            )

            # Save task to Needs_Action/
            needs_action_folder = self.vault_path / "Needs_Action"
            needs_action_folder.mkdir(exist_ok=True)

            task_file = needs_action_folder / f"task-{task.id}.md"
            task_file.write_text(task.to_markdown(), encoding="utf-8")

            logger.info(f"Created task {task.id} from email: {email_dict['subject']}")
            return task.id

        except Exception as e:
            logger.error(f"Failed to create task from email: {e}")
            return None

    def mark_as_read(self, email_id: str):
        """
        Mark email as read in Gmail.

        Args:
            email_id: Gmail message ID
        """
        mail = self.connect()
        if not mail:
            return

        try:
            mail.select("INBOX")
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            logger.info(f"Marked email {email_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

    def check_gmail(self) -> int:
        """
        Check Gmail for new emails and create tasks.

        This is the main entry point for Gmail polling.

        Returns:
            Number of tasks created
        """
        logger.info("Checking Gmail for new emails...")

        # Fetch unread emails
        emails = self.fetch_unread_emails()

        if not emails:
            logger.info("No new emails to process")
            return 0

        # Create tasks for each email
        tasks_created = 0
        for email_dict in emails:
            task_id = self.create_task_from_email(email_dict)

            if task_id:
                # Mark email as read after successful task creation
                self.mark_as_read(email_dict['id'])
                tasks_created += 1

        logger.info(f"Gmail check complete. Created {tasks_created} tasks from {len(emails)} emails.")
        return tasks_created

    def run_once(self) -> int:
        """
        Run one cycle of email checking.

        Returns:
            Number of tasks created
        """
        return self.check_gmail()

    def start(self):
        """
        Start Gmail watcher (for manual testing).
        """
        logger.info("Starting Gmail watcher...")
        tasks_created = self.check_gmail()
        logger.info(f"Gmail watcher completed. Tasks created: {tasks_created}")


def main():
    """CLI entry point for testing Gmail watcher."""
    from ai_employee.config import Config

    config = Config()
    watcher = GmailWatcher(vault_path=config.vault_path)

    # Check credentials
    if not watcher.email_address or not watcher.password:
        print("ERROR: Gmail credentials not configured")
        print("Set environment variables:")
        print("  GMAIL_EMAIL=your-email@gmail.com")
        print("  GMAIL_PASSWORD=your-app-password")
        print("\nTo create Gmail App Password:")
        print("  1. Go to https://myaccount.google.com/apppasswords")
        print("  2. Generate new app password")
        print("  3. Use that password (not your regular Gmail password)")
        return 1

    print(f"Gmail Watcher")
    print(f"Email: {watcher.email_address}")
    print(f"Vault: {config.vault_path}")
    print("-" * 60)

    watcher.start()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
