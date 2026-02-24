#!/usr/bin/env python3
"""
AI Employee Runner (Silver Tier - Production)

Fully automated workflow:
1. Capture inputs (files, emails)
2. Generate plans using reasoning skill
3. Route to approval workflow
4. Execute approved actions
5. Log everything

NO manual intervention required.
NO subprocess CLI calls.
ALL AI logic in Agent Skills.
"""

import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from ai_employee.config import Config
from ai_employee.watchers.file_watcher import FileWatcher
from ai_employee.watchers.gmail_watcher import GmailWatcher
from ai_employee.skills.reasoning_skill import ReasoningSkill
from ai_employee.skills.approval_skill import ApprovalSkill
from ai_employee.skills.linkedin_execution_skill import LinkedInExecutionSkill
from ai_employee.models.task import Task
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class AIEmployeeRunner:
    """
    Production AI Employee Runner (Silver Tier).

    Fully automated workflow with:
    - Two watchers (file + Gmail)
    - Claude reasoning loop (generates Plan.md)
    - Human-in-the-loop approval
    - MCP execution
    - OS-level scheduling
    """

    def __init__(self, config: Config):
        """Initialize runner with all components."""
        self.config = config
        self.vault_path = config.vault_path

        # Initialize watchers
        self.file_watcher = FileWatcher(
            watch_folder=config.watch_folder,
            vault_path=config.vault_path,
        )
        self.gmail_watcher = GmailWatcher(vault_path=config.vault_path)

        # Initialize skills
        self.reasoning_skill = ReasoningSkill(vault_path=config.vault_path)
        self.approval_skill = ApprovalSkill(vault_path=config.vault_path)
        self.linkedin_skill = LinkedInExecutionSkill(vault_path=config.vault_path)

        # Paths
        self.needs_action_folder = self.vault_path / "Needs_Action"
        self.waiting_approval_folder = self.vault_path / "Waiting_Approval"
        self.done_folder = self.vault_path / "Done"

        # Statistics
        self.stats = {
            "files_captured": 0,
            "emails_captured": 0,
            "plans_generated": 0,
            "approvals_processed": 0,
            "linkedin_posts": 0,
            "errors": 0,
        }

        logger.info("AI Employee Runner initialized (Silver Tier - Production)")

    def step1_capture_inputs(self) -> int:
        """
        Step 1: Capture inputs from all watchers.

        Returns:
            Total inputs captured
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Capturing inputs")
        logger.info("=" * 60)

        total = 0

        # Capture files
        try:
            files = self.file_watcher.run_once()
            self.stats["files_captured"] = files
            logger.info(f"Files captured: {files}")
            total += files
        except Exception as e:
            logger.error(f"Error capturing files: {e}")
            self.stats["errors"] += 1

        # Capture emails
        try:
            emails = self.gmail_watcher.run_once()
            self.stats["emails_captured"] = emails
            logger.info(f"Emails captured: {emails}")
            total += emails
        except Exception as e:
            logger.error(f"Error capturing emails: {e}")
            self.stats["errors"] += 1

        logger.info(f"Total inputs captured: {total}")
        return total

    def step2_generate_plans(self) -> int:
        """
        Step 2: Generate plans for pending tasks using reasoning skill.

        Automatically:
        - Reads tasks from Needs_Action/
        - Calls reasoning_skill.generate_plan()
        - Creates Plan.md files
        - Routes to approval or done

        Returns:
            Number of plans generated
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Generating plans (Claude reasoning)")
        logger.info("=" * 60)

        # Get pending tasks
        if not self.needs_action_folder.exists():
            logger.info("No Needs_Action folder")
            return 0

        task_files = list(self.needs_action_folder.glob("task-*.md"))

        if not task_files:
            logger.info("No pending tasks")
            return 0

        logger.info(f"Found {len(task_files)} pending tasks")
        plans_generated = 0

        for task_file in task_files:
            try:
                # Load task
                task = Task.from_markdown(task_file.read_text(encoding="utf-8"))
                logger.info(f"Processing task: {task.id} - {task.title}")

                # Generate plan using reasoning skill
                plan, needs_approval = self.reasoning_skill.generate_plan(task)

                # Save plan
                plan_path = self.reasoning_skill.save_plan(plan, task_title=task.title)
                logger.info(f"Plan generated: {plan_path}")

                plans_generated += 1

                # Route based on approval requirement
                if needs_approval:
                    # Create approval request
                    approval_path = self.approval_skill.create_approval_request(task, plan)
                    logger.info(f"Approval required: {approval_path}")

                    # Move task to Waiting_Approval
                    dest = self.waiting_approval_folder / task_file.name
                    task_file.rename(dest)
                    logger.info(f"Task moved to Waiting_Approval: {task.id}")
                else:
                    # No approval needed, move to Done
                    dest = self.done_folder / task_file.name
                    task_file.rename(dest)
                    logger.info(f"Task completed (no approval needed): {task.id}")

            except Exception as e:
                logger.error(f"Error processing task {task_file.name}: {e}")
                self.stats["errors"] += 1
                continue

        self.stats["plans_generated"] = plans_generated
        logger.info(f"Plans generated: {plans_generated}")
        return plans_generated

    def step3_process_approvals(self) -> Dict[str, str]:
        """
        Step 3: Process pending approvals.

        Checks for APPROVED.txt or REJECTED.txt files.
        Moves approved tasks to execution queue.

        Returns:
            Dictionary of task_id -> status
        """
        logger.info("=" * 60)
        logger.info("STEP 3: Processing approvals")
        logger.info("=" * 60)

        try:
            results = self.approval_skill.process_pending_approvals()

            if not results:
                logger.info("No approvals to process")
            else:
                logger.info(f"Approvals processed: {len(results)}")
                for task_id, status in results.items():
                    logger.info(f"  {task_id}: {status}")

            self.stats["approvals_processed"] = len(results)
            return results

        except Exception as e:
            logger.error(f"Error processing approvals: {e}")
            self.stats["errors"] += 1
            return {}

    def step4_execute_approved_actions(self) -> int:
        """
        Step 4: Execute approved actions.

        For LinkedIn posts:
        - Reads from LinkedIn_Posts/
        - Calls linkedin_execution_skill
        - Posts via real LinkedIn API
        - Moves to Done

        Returns:
            Number of actions executed
        """
        logger.info("=" * 60)
        logger.info("STEP 4: Executing approved actions")
        logger.info("=" * 60)

        executed = 0

        # Execute LinkedIn posts
        try:
            pending_posts = self.linkedin_skill.get_pending_posts()

            if not pending_posts:
                logger.info("No pending LinkedIn posts")
            else:
                logger.info(f"Found {len(pending_posts)} pending LinkedIn posts")

                for task_id in pending_posts:
                    try:
                        logger.info(f"Executing LinkedIn post: {task_id}")
                        result = self.linkedin_skill.execute_approved_post(task_id)

                        if result["success"]:
                            logger.info(f"✅ Posted successfully: {result['message']}")
                            executed += 1
                        else:
                            logger.error(f"❌ Failed to post: {result['message']}")
                            self.stats["errors"] += 1

                    except Exception as e:
                        logger.error(f"Error executing post {task_id}: {e}")
                        self.stats["errors"] += 1
                        continue

            self.stats["linkedin_posts"] = executed

        except Exception as e:
            logger.error(f"Error in LinkedIn execution: {e}")
            self.stats["errors"] += 1

        logger.info(f"Actions executed: {executed}")
        return executed

    def run(self) -> Dict[str, int]:
        """
        Run complete automated workflow.

        Returns:
            Statistics dictionary
        """
        start_time = datetime.now()

        logger.info("\n" + "=" * 80)
        logger.info("AI EMPLOYEE - SILVER TIER (PRODUCTION)")
        logger.info("=" * 80)
        logger.info(f"Run started: {start_time.isoformat()}")
        logger.info(f"Vault: {self.vault_path}")
        logger.info("=" * 80 + "\n")

        try:
            # Step 1: Capture inputs
            self.step1_capture_inputs()

            # Step 2: Generate plans
            self.step2_generate_plans()

            # Step 3: Process approvals
            self.step3_process_approvals()

            # Step 4: Execute approved actions
            self.step4_execute_approved_actions()

        except Exception as e:
            logger.error(f"Fatal error in workflow: {e}")
            self.stats["errors"] += 1

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Files captured:      {self.stats['files_captured']}")
        logger.info(f"Emails captured:     {self.stats['emails_captured']}")
        logger.info(f"Plans generated:     {self.stats['plans_generated']}")
        logger.info(f"Approvals processed: {self.stats['approvals_processed']}")
        logger.info(f"LinkedIn posts:      {self.stats['linkedin_posts']}")
        logger.info(f"Errors:              {self.stats['errors']}")
        logger.info("=" * 80 + "\n")

        return self.stats


def main():
    """Main entry point for automated runner."""
    try:
        # Load configuration
        config = Config()

        # Validate vault
        if not config.vault_path.exists():
            logger.error(f"Vault not found at {config.vault_path}")
            print(f"ERROR: Vault not found at {config.vault_path}")
            print("Run: python -m ai_employee init")
            return 1

        # Run workflow
        runner = AIEmployeeRunner(config)
        stats = runner.run()

        # Exit with error code if errors occurred
        return 1 if stats["errors"] > 0 else 0

    except KeyboardInterrupt:
        logger.info("Stopped by user")
        print("\n\nStopped by user")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFATAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
