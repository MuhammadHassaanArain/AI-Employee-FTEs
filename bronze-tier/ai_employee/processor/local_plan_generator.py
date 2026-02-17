"""
Local Plan Generator (Bronze Tier)

Generates action plans locally without external API calls.
This is a rule-based system that processes tasks deterministically.
"""

from datetime import datetime
from ai_employee.models.task import Task
from ai_employee.models.plan import Plan
from ai_employee.processor.handbook_parser import HandbookParser


class LocalPlanGenerator:
    """
    Local-only plan generator for Bronze Tier AI Employee.

    This class generates action plans without any external API calls.
    All processing is done locally using rule-based logic.
    """

    def __init__(self, handbook_parser: HandbookParser):
        """
        Initialize local plan generator

        Args:
            handbook_parser: Parser for Company Handbook rules
        """
        self.handbook_parser = handbook_parser

    def generate_plan(self, task: Task) -> Plan:
        """
        Generate an action plan for a task using local processing only.

        Args:
            task: Task object to generate plan for

        Returns:
            Plan object with steps, approval checkpoints, and warnings
        """
        start_time = datetime.utcnow()

        # Analyze task content
        content_lower = task.content.lower()
        title_lower = task.title.lower()
        combined_text = f"{title_lower} {content_lower}"

        # Initialize plan components
        steps = []
        approval_checkpoints = []
        warnings = []
        handbook_rules_applied = []

        # Determine task type and generate appropriate steps
        task_type = self._identify_task_type(combined_text)

        if task_type == "email":
            steps = self._generate_email_steps(task)
            approval_checkpoints = [3]  # Approval before sending
            handbook_rules_applied.append("[HIGH] Ask for approval before sending emails")
            warnings.append("Email sending requires human approval per company policy")

        elif task_type == "meeting":
            steps = self._generate_meeting_steps(task)
            handbook_rules_applied.append("[MEDIUM] Verify meeting details and attendees")

        elif task_type == "whatsapp":
            steps = self._generate_messaging_steps(task, "WhatsApp")
            approval_checkpoints = [len(steps) - 1]  # Last step (sending) requires approval
            handbook_rules_applied.append("[HIGH] Ask for approval before sending messages")

        elif task_type == "file_processing":
            steps = self._generate_file_processing_steps(task)
            handbook_rules_applied.append("[CRITICAL] Never delete original files")
            warnings.append("Original files must be preserved")

        elif task_type == "summary":
            steps = self._generate_summary_steps(task)
            handbook_rules_applied.append("[MEDIUM] Summaries under 200 words")
            handbook_rules_applied.append("[LOW] Use bullet points when possible")

        elif task_type == "request":
            steps = self._generate_request_steps(task)
            handbook_rules_applied.append("[CRITICAL] Never delete original files")

        elif task_type == "test":
            steps = self._generate_test_steps(task)
            warnings.append("This is a test file - no production actions will be taken")

        else:
            # Content-aware generic task
            steps = self._generate_content_aware_steps(task)
            handbook_rules_applied.append("[CRITICAL] Never delete original files")

        # Calculate generation time
        end_time = datetime.utcnow()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Create plan
        plan = Plan(
            task_id=task.id,
            steps=steps,
            approval_checkpoints=approval_checkpoints,
            handbook_rules_applied=handbook_rules_applied,
            warnings=warnings,
            model_used="local-bronze-tier",
            generation_time_ms=generation_time_ms,
        )

        return plan

    def _identify_task_type(self, text: str) -> str:
        """
        Identify task type from content with improved pattern matching.
        Patterns are checked in priority order (most specific first).
        """

        # Email patterns (highest priority - very specific)
        email_patterns = [
            "subject:", "to:", "from:", "cc:", "bcc:",
            "send email", "compose email", "draft email",
            "email to", "reply to", "forward"
        ]
        if any(pattern in text for pattern in email_patterns):
            return "email"

        # Summary/Report patterns (high priority - check before generic requests)
        # These are specific action verbs that indicate summarization
        summary_patterns = [
            "summarize", "summary of", "tldr", "brief overview",
            "create summary", "provide summary", "key points from",
            "please summarize", "can you summarize"
        ]
        if any(pattern in text for pattern in summary_patterns):
            return "summary"

        # Meeting patterns (high priority - specific actions)
        meeting_patterns = [
            "schedule meeting", "book meeting", "arrange meeting",
            "meeting with", "join meeting", "attend meeting",
            "zoom", "teams meeting", "conference call",
            "calendar invite", "meeting invite"
        ]
        if any(pattern in text for pattern in meeting_patterns):
            return "meeting"

        # Messaging patterns (high priority - specific platforms)
        messaging_patterns = [
            "whatsapp", "send message", "text message", "sms",
            "slack message", "telegram", "send via"
        ]
        if any(pattern in text for pattern in messaging_patterns):
            return "whatsapp"

        # File processing patterns (medium-high priority)
        file_patterns = [
            "process file", "upload file", "download file",
            "file attachment", "attached file", "pdf", "docx", "xlsx"
        ]
        if any(pattern in text for pattern in file_patterns):
            return "file_processing"

        # Request/Action patterns (medium priority - after specific task types)
        # Only match if no more specific pattern was found
        request_patterns = [
            "please", "could you", "can you", "would you",
            "need you to", "requesting", "request that",
            "help me", "assist with", "i need"
        ]
        if any(pattern in text for pattern in request_patterns):
            return "request"

        # Test patterns (low priority - only for explicit tests)
        test_patterns = [
            "test file", "testing the", "this is a test",
            "validation test", "test case"
        ]
        if any(pattern in text for pattern in test_patterns):
            return "test"

        # Broader meeting indicators (after specific checks)
        if any(word in text for word in ["meeting", "agenda", "attendee"]):
            return "meeting"

        # Default to content-aware generic
        return "generic"

    def _generate_email_steps(self, task: Task) -> list:
        """Generate steps for email tasks"""
        return [
            "Review email content and verify recipient addresses",
            "Check for sensitive information or attachments",
            "Draft email with appropriate subject line and formatting",
            "Request human approval before sending",
            "Send email after approval is granted",
            "Log email sent in activity log",
            "Archive task in Done folder"
        ]

    def _generate_messaging_steps(self, task: Task, platform: str) -> list:
        """Generate steps for messaging tasks"""
        return [
            f"Review {platform} message content",
            "Verify recipient contact information",
            "Check message tone and formatting",
            f"Request approval before sending {platform} message",
            f"Send message via {platform} after approval",
            "Log message sent in activity log"
        ]

    def _generate_file_processing_steps(self, task: Task) -> list:
        """Generate steps for file processing tasks"""
        return [
            "Read and analyze file content",
            "Identify file type and processing requirements",
            "Extract relevant information from file",
            "Generate structured output",
            "Write processed result to Done folder",
            "Preserve original file (do not delete)",
            "Update activity log with processing status"
        ]

    def _generate_summary_steps(self, task: Task) -> list:
        """Generate steps for summarization tasks"""
        return [
            "Read full content of source material",
            "Identify key points and main themes",
            "Create concise summary (under 200 words)",
            "Format summary with bullet points",
            "Review summary for accuracy and completeness",
            "Save summary to Done folder"
        ]

    def _generate_test_steps(self, task: Task) -> list:
        """Generate steps for test/validation tasks"""
        return [
            "Confirm file detection system is working",
            "Verify file reading capabilities",
            "Validate task processing pipeline",
            "Generate structured output in required format",
            "Write processed result to Done folder",
            "Mark test as successful in logs"
        ]

    def _generate_generic_steps(self, task: Task) -> list:
        """Generate steps for generic tasks"""
        return [
            "Analyze task content and requirements",
            "Identify task type and priority",
            "Determine required actions",
            "Execute actions following company handbook rules",
            "Document results and outcomes",
            "Move completed task to Done folder",
            "Update activity log"
        ]

    def _generate_meeting_steps(self, task: Task) -> list:
        """Generate steps for meeting-related tasks"""
        content_lower = task.content.lower()

        steps = ["Review meeting request details"]

        # Check for scheduling
        if any(word in content_lower for word in ["schedule", "when", "time", "date"]):
            steps.append("Identify proposed date and time")
            steps.append("Check calendar availability")

        # Check for attendees
        if any(word in content_lower for word in ["attendee", "participant", "invite", "team", "@"]):
            steps.append("Compile list of required attendees")
            steps.append("Verify contact information for all participants")

        # Check for agenda
        if any(word in content_lower for word in ["agenda", "topic", "discuss", "review"]):
            steps.append("Extract meeting agenda items")

        steps.extend([
            "Prepare meeting invitation with all details",
            "Send calendar invites to all attendees",
            "Log meeting scheduled in activity log"
        ])

        return steps

    def _generate_request_steps(self, task: Task) -> list:
        """Generate steps for request/action tasks"""
        content_lower = task.content.lower()

        steps = ["Read and understand the request"]

        # Identify what's being requested
        if "please" in content_lower or "could you" in content_lower:
            steps.append("Identify specific action requested")

        # Check for urgency
        if any(word in content_lower for word in ["urgent", "asap", "immediately", "priority"]):
            steps.append("Note urgency level and prioritize accordingly")

        # Check for dependencies
        if any(word in content_lower for word in ["after", "before", "once", "when", "if"]):
            steps.append("Identify any dependencies or prerequisites")

        steps.extend([
            "Break down request into actionable sub-tasks",
            "Execute each sub-task in order",
            "Verify completion of all requested items",
            "Document outcome and any issues encountered",
            "Mark task as complete"
        ])

        return steps

    def _generate_content_aware_steps(self, task: Task) -> list:
        """
        Generate content-aware steps based on actual task content.
        This replaces the static generic steps with dynamic analysis.
        """
        content = task.content.strip()
        content_lower = content.lower()
        lines = content.split("\n")

        steps = []

        # Step 1: Always start with reading/understanding
        if len(content) > 200:
            steps.append(f"Read and analyze the full task content ({len(content)} characters)")
        else:
            steps.append("Read and understand the task requirements")

        # Step 2: Identify key elements based on content
        if any(char in content for char in ["?", "how", "what", "why", "when", "where"]):
            steps.append("Identify questions that need to be answered")

        if any(word in content_lower for word in ["create", "make", "build", "generate", "write"]):
            steps.append("Determine what needs to be created or generated")

        if any(word in content_lower for word in ["update", "modify", "change", "edit", "fix"]):
            steps.append("Identify what needs to be updated or modified")

        if any(word in content_lower for word in ["review", "check", "verify", "validate", "confirm"]):
            steps.append("Perform required review or validation")

        # Step 3: Check for specific content types
        if "@" in content or "email" in content_lower:
            steps.append("Extract any email addresses or contact information")

        if any(word in content_lower for word in ["deadline", "due", "by", "before"]):
            steps.append("Note any deadlines or time constraints")

        if len(lines) > 5:
            steps.append(f"Process each of the {len(lines)} items or sections")

        # Step 4: Action steps based on content
        if ":" in content:  # Structured content
            steps.append("Process structured information (labels, fields, sections)")

        # Step 5: Always include completion steps
        steps.extend([
            "Execute identified actions following company handbook rules",
            "Document results and any important findings",
            "Save completed work to Done folder",
            "Update activity log with task completion"
        ])

        return steps
