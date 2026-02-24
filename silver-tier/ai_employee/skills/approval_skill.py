"""
Approval Skill (Silver Tier)

Human-in-the-loop approval workflow for sensitive actions.
This is an Agent Skill that manages approval requests.
"""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
from ai_employee.models.task import Task
from ai_employee.models.plan import Plan
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class ApprovalSkill:
    """
    Agent Skill: Human-in-the-loop approval workflow.

    Silver Tier Requirement: Approval workflow for sensitive actions.
    """

    def __init__(self, vault_path: Path, timeout_hours: int = 24):
        """
        Initialize approval skill.

        Args:
            vault_path: Path to Obsidian vault
            timeout_hours: Hours to wait before timing out approval request
        """
        self.vault_path = vault_path
        self.waiting_approval_folder = vault_path / "Waiting_Approval"
        self.approved_folder = vault_path / "Approved"
        self.rejected_folder = vault_path / "Rejected"
        self.timeout_hours = timeout_hours

        # Ensure folders exist
        self.waiting_approval_folder.mkdir(parents=True, exist_ok=True)
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.rejected_folder.mkdir(parents=True, exist_ok=True)

        logger.info("Approval Skill initialized (Silver Tier)")

    def create_approval_request(self, task: Task, plan: Plan) -> Path:
        """
        Create approval request file in Waiting_Approval folder.

        Args:
            task: Task requiring approval
            plan: Generated plan with approval checkpoints

        Returns:
            Path to approval request file
        """
        logger.info(f"Creating approval request for task: {task.id}")

        approval_filename = f"approval-{task.id}.md"
        approval_path = self.waiting_approval_folder / approval_filename

        # Format approval request
        approval_content = f"""# Approval Request

**Task ID**: {task.id}
**Task Title**: {task.title}
**Created**: {datetime.now().isoformat()}
**Timeout**: {self.timeout_hours} hours

## Task Content

{task.content}

## Generated Plan

"""
        for i, step in enumerate(plan.steps, 1):
            if i - 1 in plan.approval_checkpoints:
                approval_content += f"{i}. **[APPROVAL REQUIRED]** {step}\n"
            else:
                approval_content += f"{i}. {step}\n"

        approval_content += f"""

## Handbook Rules Applied

"""
        for rule in plan.handbook_rules:
            approval_content += f"- {rule}\n"

        approval_content += f"""

## Warnings

"""
        for warning in plan.warnings:
            approval_content += f"- {warning}\n"

        approval_content += f"""

---

## How to Approve/Reject

To **APPROVE** this action:
1. Create a file named `APPROVED.txt` in the Waiting_Approval folder
2. The system will execute the action

To **REJECT** this action:
1. Create a file named `REJECTED.txt` in the Waiting_Approval folder
2. The system will cancel the action

**Note**: This request will timeout after {self.timeout_hours} hours and be automatically rejected.
"""

        # Save approval request
        approval_path.write_text(approval_content, encoding="utf-8")

        logger.info(f"Approval request created: {approval_path}")
        return approval_path

    def check_approval_status(self, task_id: str) -> Optional[str]:
        """
        Check if approval request has been approved or rejected.

        Args:
            task_id: Task ID to check

        Returns:
            "approved", "rejected", "timeout", or None if still pending
        """
        approval_file = self.waiting_approval_folder / f"approval-{task_id}.md"

        if not approval_file.exists():
            logger.warning(f"Approval request not found: {task_id}")
            return None

        # Check for approval/rejection files
        approved_file = self.waiting_approval_folder / "APPROVED.txt"
        rejected_file = self.waiting_approval_folder / "REJECTED.txt"

        if approved_file.exists():
            logger.info(f"Task {task_id} approved by human")
            return "approved"

        if rejected_file.exists():
            logger.info(f"Task {task_id} rejected by human")
            return "rejected"

        # Check timeout
        try:
            # Get file creation time
            created_time = datetime.fromtimestamp(approval_file.stat().st_mtime)
            elapsed = datetime.now() - created_time

            if elapsed > timedelta(hours=self.timeout_hours):
                logger.warning(f"Task {task_id} approval timed out after {self.timeout_hours} hours")
                return "timeout"
        except Exception as e:
            logger.error(f"Error checking timeout for {task_id}: {e}")

        return None

    def move_to_approved(self, task_id: str):
        """
        Move approval request to Approved folder.

        Args:
            task_id: Task ID
        """
        source = self.waiting_approval_folder / f"approval-{task_id}.md"
        dest = self.approved_folder / f"approval-{task_id}.md"

        if source.exists():
            source.rename(dest)
            logger.info(f"Moved to Approved: {task_id}")

        # Clean up approval file
        approved_file = self.waiting_approval_folder / "APPROVED.txt"
        if approved_file.exists():
            approved_file.unlink()

    def move_to_rejected(self, task_id: str):
        """
        Move approval request to Rejected folder.

        Args:
            task_id: Task ID
        """
        source = self.waiting_approval_folder / f"approval-{task_id}.md"
        dest = self.rejected_folder / f"approval-{task_id}.md"

        if source.exists():
            source.rename(dest)
            logger.info(f"Moved to Rejected: {task_id}")

        # Clean up rejection file
        rejected_file = self.waiting_approval_folder / "REJECTED.txt"
        if rejected_file.exists():
            rejected_file.unlink()

    def process_pending_approvals(self) -> Dict[str, str]:
        """
        Process all pending approval requests.

        Returns:
            Dictionary mapping task_id to status (approved/rejected/timeout)
        """
        logger.info("Processing pending approvals...")

        results = {}

        # Get all approval requests
        approval_files = list(self.waiting_approval_folder.glob("approval-*.md"))

        for approval_file in approval_files:
            # Extract task ID from filename
            task_id = approval_file.stem.replace("approval-", "")

            # Check status
            status = self.check_approval_status(task_id)

            if status == "approved":
                self.move_to_approved(task_id)
                results[task_id] = "approved"
            elif status == "rejected":
                self.move_to_rejected(task_id)
                results[task_id] = "rejected"
            elif status == "timeout":
                self.move_to_rejected(task_id)
                results[task_id] = "timeout"
            # else: still pending, do nothing

        logger.info(f"Processed {len(results)} approval requests")
        return results


def main():
    """CLI entry point for testing approval skill."""
    from ai_employee.config import Config
    from ai_employee.models.task import Task
    from ai_employee.models.plan import Plan

    config = Config()
    skill = ApprovalSkill(vault_path=config.vault_path)

    # Test with dummy task and plan
    test_task = Task(
        title="Send email to client",
        content="Please send an email to client@example.com with project update.",
        source_path="/test/email.txt",
    )

    test_plan = Plan(
        task_id=test_task.id,
        task_title=test_task.title,
        task_source=test_task.source,
        action_type="email",
        steps=[
            "Draft email content",
            "Send email to client@example.com",
            "Log email sent",
        ],
        approval_required=True,
        approval_checkpoints=[1],
        handbook_rules=["[HIGH] Ask for approval before sending emails"],
        warnings=["This action will send an external email"],
    )

    # Create approval request
    approval_path = skill.create_approval_request(test_task, test_plan)
    print(f"Approval request created: {approval_path}")

    # Process pending approvals
    results = skill.process_pending_approvals()
    print(f"Approval results: {results}")


if __name__ == "__main__":
    main()
