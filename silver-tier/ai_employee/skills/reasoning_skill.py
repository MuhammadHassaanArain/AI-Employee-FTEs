"""
Reasoning Skill (Silver Tier)

Intelligent task analysis and plan generation.
Uses rule-based reasoning with pattern matching for hackathon speed.

Note: For production, this can be enhanced with Claude API integration.
"""

from pathlib import Path
from typing import Tuple, Optional, List, Dict
from ai_employee.models.task import Task
from ai_employee.models.plan import Plan
from ai_employee.utils.logger import get_logger
import re

logger = get_logger(__name__)


class ReasoningSkill:
    """
    Agent Skill: Intelligent task reasoning and plan generation.

    Silver Tier Requirement: Claude reasoning loop that generates Plan.md files.
    """

    def __init__(self, vault_path: Path):
        """
        Initialize reasoning skill.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = vault_path
        self.plans_folder = vault_path / "Plans"
        self.handbook_path = vault_path / "Company_Handbook.md"

        # Ensure Plans folder exists
        self.plans_folder.mkdir(exist_ok=True)

        # Action detection patterns
        self.action_patterns = {
            "email": [
                r'\bemail\b', r'\bsend\b.*\bemail\b', r'\breply\b', r'\brespond\b',
                r'\bmessage\b', r'\bcontact\b', r'\bnotify\b', r'\binform\b'
            ],
            "linkedin": [
                r'\blinkedin\b', r'\bpost\b.*\blinkedin\b', r'\bshare\b.*\blinkedin\b',
                r'\bpublish\b', r'\bsocial\b.*\bmedia\b'
            ],
            "payment": [
                r'\bpay\b', r'\bpayment\b', r'\binvoice\b', r'\bbill\b',
                r'\btransfer\b', r'\$\d+', r'\bmoney\b', r'\bpurchase\b'
            ],
            "delete": [
                r'\bdelete\b', r'\bremove\b', r'\berase\b', r'\bdrop\b'
            ],
            "research": [
                r'\bresearch\b', r'\binvestigate\b', r'\bfind\b.*\binformation\b',
                r'\blook\b.*\bup\b', r'\banalyze\b', r'\breview\b'
            ],
            "schedule": [
                r'\bschedule\b', r'\bmeeting\b', r'\bcalendar\b', r'\bappointment\b'
            ],
        }

        # Sensitive action keywords (require approval)
        self.sensitive_keywords = [
            'email', 'send', 'payment', 'pay', 'delete', 'remove',
            'post', 'publish', 'linkedin', 'twitter', 'social',
            'transfer', 'invoice', 'purchase'
        ]

        logger.info("Reasoning Skill initialized (Silver Tier)")

    def read_handbook(self) -> str:
        """
        Read Company Handbook for behavioral rules.

        Returns:
            Handbook content as string
        """
        if not self.handbook_path.exists():
            logger.warning("Company Handbook not found")
            return ""

        try:
            return self.handbook_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read handbook: {e}")
            return ""

    def parse_handbook_rules(self, handbook_content: str) -> List[str]:
        """
        Parse handbook rules into list.

        Args:
            handbook_content: Raw handbook content

        Returns:
            List of rule strings
        """
        rules = []

        # Extract lines that look like rules (start with -, *, or [PRIORITY])
        for line in handbook_content.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or '[' in line:
                if any(priority in line for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']):
                    rules.append(line.lstrip('-* '))

        return rules

    def detect_action_type(self, task_content: str) -> str:
        """
        Detect primary action type from task content.

        Args:
            task_content: Task content to analyze

        Returns:
            Action type: email, linkedin, payment, delete, research, schedule, or general
        """
        content_lower = task_content.lower()

        # Check each action type
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    logger.info(f"Detected action type: {action_type}")
                    return action_type

        return "general"

    def detect_sensitive_actions(self, task_content: str, handbook_rules: List[str]) -> bool:
        """
        Detect if task requires human approval.

        Args:
            task_content: Task content to analyze
            handbook_rules: List of handbook rules

        Returns:
            True if approval required, False otherwise
        """
        content_lower = task_content.lower()

        # Check sensitive keywords
        for keyword in self.sensitive_keywords:
            if keyword in content_lower:
                logger.info(f"Sensitive action detected: {keyword}")
                return True

        # Check handbook rules for approval requirements
        for rule in handbook_rules:
            if 'approval' in rule.lower() or 'ask' in rule.lower():
                # Check if rule applies to this task
                rule_keywords = re.findall(r'\b\w+\b', rule.lower())
                for keyword in rule_keywords:
                    if keyword in content_lower and len(keyword) > 3:
                        logger.info(f"Handbook rule requires approval: {rule}")
                        return True

        return False

    def extract_key_entities(self, task_content: str) -> Dict[str, List[str]]:
        """
        Extract key entities from task content.

        Args:
            task_content: Task content

        Returns:
            Dictionary of entity types and values
        """
        entities = {
            "emails": [],
            "urls": [],
            "amounts": [],
            "dates": [],
            "names": [],
        }

        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', task_content)
        entities["emails"] = emails

        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', task_content)
        entities["urls"] = urls

        # Extract amounts
        amounts = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', task_content)
        entities["amounts"] = amounts

        # Extract dates (simple patterns)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', task_content)
        entities["dates"] = dates

        return entities

    def generate_steps(self, task: Task, action_type: str, entities: Dict) -> List[str]:
        """
        Generate action steps based on task analysis.

        Args:
            task: Task object
            action_type: Detected action type
            entities: Extracted entities

        Returns:
            List of action steps
        """
        steps = []

        # Add context-aware steps based on action type
        if action_type == "email":
            steps.append("Review email content and recipients")
            if entities["emails"]:
                steps.append(f"Verify recipient addresses: {', '.join(entities['emails'][:3])}")
            steps.append("Draft email message")
            steps.append("Request approval before sending")
            steps.append("Send email via MCP server")
            steps.append("Log email sent in activity log")

        elif action_type == "linkedin":
            steps.append("Review post content for appropriateness")
            steps.append("Check company social media guidelines")
            steps.append("Request approval before posting")
            steps.append("Post to LinkedIn via MCP server")
            steps.append("Monitor post engagement")

        elif action_type == "payment":
            steps.append("Verify payment details and amount")
            if entities["amounts"]:
                steps.append(f"Confirm amount: {entities['amounts'][0]}")
            steps.append("Check budget and authorization limits")
            steps.append("Request approval from authorized person")
            steps.append("Process payment via approved method")
            steps.append("Record transaction in financial system")

        elif action_type == "research":
            steps.append("Define research scope and objectives")
            steps.append("Identify reliable information sources")
            if entities["urls"]:
                steps.append(f"Review provided resources: {len(entities['urls'])} links")
            steps.append("Gather and analyze information")
            steps.append("Summarize findings in structured format")
            steps.append("Document sources and references")

        elif action_type == "schedule":
            steps.append("Review meeting requirements and attendees")
            if entities["dates"]:
                steps.append(f"Check proposed dates: {', '.join(entities['dates'])}")
            steps.append("Check calendar availability")
            steps.append("Send meeting invitations")
            steps.append("Add to calendar with reminders")

        elif action_type == "delete":
            steps.append("Identify items to be deleted")
            steps.append("Verify deletion is authorized")
            steps.append("Create backup before deletion")
            steps.append("Request approval for deletion")
            steps.append("Execute deletion")
            steps.append("Confirm deletion and log action")

        else:  # general
            steps.append("Analyze task requirements")
            steps.append("Break down into actionable subtasks")
            steps.append("Execute each subtask in sequence")
            steps.append("Verify completion")
            steps.append("Document results")

        return steps

    def identify_approval_checkpoints(self, steps: List[str], needs_approval: bool) -> List[int]:
        """
        Identify which steps require approval.

        Args:
            steps: List of action steps
            needs_approval: Whether task needs approval

        Returns:
            List of step indices requiring approval
        """
        if not needs_approval:
            return []

        approval_checkpoints = []

        # Find steps that mention approval or sensitive actions
        for i, step in enumerate(steps):
            step_lower = step.lower()
            if any(keyword in step_lower for keyword in ['approval', 'send', 'post', 'delete', 'payment', 'transfer']):
                approval_checkpoints.append(i)

        # If no explicit approval steps found but approval needed, add before last step
        if not approval_checkpoints and needs_approval:
            approval_checkpoints.append(len(steps) - 2 if len(steps) > 1 else 0)

        return approval_checkpoints

    def generate_warnings(self, task: Task, action_type: str, entities: Dict) -> List[str]:
        """
        Generate warnings based on task analysis.

        Args:
            task: Task object
            action_type: Detected action type
            entities: Extracted entities

        Returns:
            List of warning messages
        """
        warnings = []

        # Action-specific warnings
        if action_type == "email" and not entities["emails"]:
            warnings.append("No email addresses detected in task - verify recipients")

        if action_type == "payment":
            if entities["amounts"]:
                amount_str = entities["amounts"][0]
                # Extract numeric value
                amount_num = float(re.sub(r'[^\d.]', '', amount_str))
                if amount_num > 1000:
                    warnings.append(f"High-value payment detected: {amount_str} - requires senior approval")
            else:
                warnings.append("Payment amount not specified - verify before processing")

        if action_type == "delete":
            warnings.append("Deletion is irreversible - ensure backup exists before proceeding")

        if action_type == "linkedin" or action_type == "email":
            warnings.append("External communication - review for company policy compliance")

        # Source-specific warnings
        if task.source == "gmail":
            warnings.append("Task originated from email - verify sender authenticity")

        return warnings

    def generate_plan(self, task: Task) -> Tuple[Plan, bool]:
        """
        Generate Plan.md using intelligent reasoning.

        Args:
            task: Task object to generate plan for

        Returns:
            Tuple of (Plan object, needs_approval boolean)
        """
        logger.info(f"Generating plan for task: {task.id}")

        # Read handbook
        handbook_content = self.read_handbook()
        handbook_rules = self.parse_handbook_rules(handbook_content)

        # Analyze task
        action_type = self.detect_action_type(task.content)
        entities = self.extract_key_entities(task.content)
        needs_approval = self.detect_sensitive_actions(task.content, handbook_rules)

        # Generate steps
        steps = self.generate_steps(task, action_type, entities)

        # Identify approval checkpoints
        approval_checkpoints = self.identify_approval_checkpoints(steps, needs_approval)

        # Generate warnings
        warnings = self.generate_warnings(task, action_type, entities)

        # Filter applicable handbook rules
        applicable_rules = []
        for rule in handbook_rules:
            rule_lower = rule.lower()
            if action_type in rule_lower or any(keyword in rule_lower for keyword in ['approval', 'ask', 'critical', 'high']):
                applicable_rules.append(rule)

        # Create plan
        plan = Plan(
            task_id=task.id,
            steps=steps,
            approval_checkpoints=approval_checkpoints,
            handbook_rules_applied=applicable_rules[:5],  # Limit to 5 most relevant
            warnings=warnings,
        )

        logger.info(f"Plan generated. Action type: {action_type}, Needs approval: {needs_approval}, Steps: {len(steps)}")
        return plan, needs_approval

    def save_plan(self, plan: Plan, task_title: str = "") -> Path:
        """
        Save Plan.md to Plans folder.

        Args:
            plan: Plan object to save
            task_title: Task title for plan filename

        Returns:
            Path to saved plan file
        """
        plan_filename = f"plan-{plan.task_id}.md"
        plan_path = self.plans_folder / plan_filename

        # Convert plan to markdown
        plan_content = plan.to_markdown(task_title=task_title)

        # Save to file
        plan_path.write_text(plan_content, encoding="utf-8")

        logger.info(f"Plan saved: {plan_path}")
        return plan_path

    def process_task(self, task: Task) -> Tuple[Plan, bool, Path]:
        """
        Full reasoning workflow: generate plan and save.

        Args:
            task: Task to process

        Returns:
            Tuple of (Plan, needs_approval, plan_path)
        """
        logger.info(f"Processing task with reasoning skill: {task.id}")

        # Generate plan
        plan, needs_approval = self.generate_plan(task)

        # Save plan
        plan_path = self.save_plan(plan, task_title=task.title)

        return plan, needs_approval, plan_path


def main():
    """CLI entry point for testing reasoning skill."""
    from ai_employee.config import Config
    from ai_employee.models.task import Task

    config = Config()
    skill = ReasoningSkill(vault_path=config.vault_path)

    # Test with various task types
    test_tasks = [
        Task(
            title="Send email to client",
            content="Please send an email to client@example.com with project update. The project is on track and we expect delivery by March 15th.",
            source="file",
        ),
        Task(
            title="Post LinkedIn update",
            content="Create a LinkedIn post about our new product launch. Highlight the key features and benefits.",
            source="file",
        ),
        Task(
            title="Research competitors",
            content="Research top 3 competitors in the AI automation space. Focus on their pricing and features.",
            source="file",
        ),
    ]

    for test_task in test_tasks:
        print(f"\n{'='*60}")
        print(f"Task: {test_task.title}")
        print(f"{'='*60}")

        plan, needs_approval, plan_path = skill.process_task(test_task)

        print(f"Plan generated: {plan_path}")
        print(f"Needs approval: {needs_approval}")
        print(f"Steps: {len(plan.steps)}")
        print(f"Warnings: {len(plan.warnings)}")

        if plan.warnings:
            print("\nWarnings:")
            for warning in plan.warnings:
                print(f"  - {warning}")


if __name__ == "__main__":
    main()
