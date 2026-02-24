#!/usr/bin/env python3
"""
LinkedIn Execution Skill

Handles execution of approved LinkedIn posts.
Integrates with LinkedInPostSkill and approval workflow.
"""

from pathlib import Path
from typing import Dict, Optional
from ai_employee.skills.linkedin_post_skill import LinkedInPostSkill
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class LinkedInExecutionSkill:
    """
    Executes approved LinkedIn posts.

    Integrates with:
    - ApprovalSkill for workflow
    - LinkedInPostSkill for API calls
    - Plan.md for content
    """

    def __init__(self, vault_path: Path):
        """
        Initialize LinkedIn execution skill.

        Args:
            vault_path: Path to vault directory
        """
        self.vault_path = Path(vault_path)
        self.linkedin_posts_dir = self.vault_path / "LinkedIn_Posts"
        self.plans_dir = self.vault_path / "Plans"
        self.done_dir = self.vault_path / "Done"

        # Initialize LinkedIn skill
        try:
            self.linkedin_skill = LinkedInPostSkill()
            logger.info("LinkedIn execution skill initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn skill: {e}")
            self.linkedin_skill = None

    def execute_approved_post(self, task_id: str) -> Dict[str, any]:
        """
        Execute an approved LinkedIn post.

        Args:
            task_id: Task ID

        Returns:
            Execution result dictionary
        """
        result = {
            "success": False,
            "task_id": task_id,
            "message": "",
            "post_id": None,
        }

        # Check if LinkedIn is configured
        if not self.linkedin_skill:
            result["message"] = "LinkedIn not configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET."
            logger.error(result["message"])
            return result

        # Check authentication
        if not self.linkedin_skill.is_authenticated():
            result["message"] = "LinkedIn not authenticated. Run OAuth setup first."
            logger.error(result["message"])
            return result

        # Find post content
        post_file = self.linkedin_posts_dir / f"post-{task_id}.md"
        if not post_file.exists():
            result["message"] = f"Post file not found: {post_file}"
            logger.error(result["message"])
            return result

        try:
            # Read post content
            content = post_file.read_text(encoding="utf-8")

            # Remove markdown header if present
            if content.startswith("#"):
                lines = content.split("\n")
                # Skip header lines
                content_lines = []
                in_header = True
                for line in lines:
                    if in_header and line.strip() and not line.startswith("#"):
                        in_header = False
                    if not in_header:
                        content_lines.append(line)
                content = "\n".join(content_lines).strip()

            # Post to LinkedIn
            logger.info(f"Posting to LinkedIn: {task_id}")
            success, message = self.linkedin_skill.publish(content)

            result["success"] = success
            result["message"] = message

            if success:
                # Extract post ID from message
                if "Post ID:" in message:
                    post_id = message.split("Post ID:")[-1].strip()
                    result["post_id"] = post_id

                logger.info(f"Successfully posted to LinkedIn: {task_id}")

                # Move task to Done
                self._move_to_done(task_id)
            else:
                logger.error(f"Failed to post to LinkedIn: {message}")

            return result

        except Exception as e:
            result["message"] = f"Error executing LinkedIn post: {e}"
            logger.error(result["message"])
            return result

    def _move_to_done(self, task_id: str):
        """
        Move completed task files to Done folder.

        Args:
            task_id: Task ID
        """
        try:
            # Move post file
            post_file = self.linkedin_posts_dir / f"post-{task_id}.md"
            if post_file.exists():
                done_post = self.done_dir / f"post-{task_id}.md"
                post_file.rename(done_post)
                logger.info(f"Moved post to Done: {done_post}")

            # Move plan file
            plan_file = self.plans_dir / f"plan-{task_id}.md"
            if plan_file.exists():
                done_plan = self.done_dir / f"plan-{task_id}.md"
                plan_file.rename(done_plan)
                logger.info(f"Moved plan to Done: {done_plan}")

        except Exception as e:
            logger.error(f"Error moving files to Done: {e}")

    def get_pending_posts(self) -> list:
        """
        Get list of pending LinkedIn posts (approved but not executed).

        Returns:
            List of task IDs
        """
        if not self.linkedin_posts_dir.exists():
            return []

        pending = []
        for post_file in self.linkedin_posts_dir.glob("post-*.md"):
            task_id = post_file.stem.replace("post-", "")
            pending.append(task_id)

        return pending
