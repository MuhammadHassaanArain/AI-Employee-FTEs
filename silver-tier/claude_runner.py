#!/usr/bin/env python3
"""
Claude Code Runner (Silver Tier - Integrated)

Single command that runs the entire AI Employee workflow:
1. File watcher - check Inbox/ for new files
2. Gmail watcher - check for new emails
3. Reasoning skill - generate plans for tasks
4. Approval skill - process pending approvals
5. MCP server - execute approved tasks
6. Mark tasks Done

Usage:
    python claude_runner.py
"""

import sys
from pathlib import Path
from typing import List, Dict
from ai_employee.config import Config
from ai_employee.watchers.file_watcher import FileWatcher
from ai_employee.watchers.gmail_watcher import GmailWatcher
from ai_employee.processor.task_processor import TaskProcessor
from ai_employee.models.task import Task
from ai_employee.skills.reasoning_skill import ReasoningSkill
from ai_employee.skills.approval_skill import ApprovalSkill
from ai_employee.mcp.mcp_server import MCPServer
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class IntegratedRunner:
    """
    Integrated runner for Silver Tier AI Employee.

    Runs complete workflow in single command.
    """

    def __init__(self, config: Config):
        """
        Initialize integrated runner.

        Args:
            config: Configuration object
        """
        self.config = config
        self.vault_path = config.vault_path

        # Initialize components
        self.file_watcher = FileWatcher(
            watch_folder=config.watch_folder,
            vault_path=config.vault_path,
        )
        self.gmail_watcher = GmailWatcher(vault_path=config.vault_path)
        self.task_processor = TaskProcessor(config.vault_path)
        self.reasoning_skill = ReasoningSkill(config.vault_path)
        self.approval_skill = ApprovalSkill(config.vault_path)
        self.mcp_server = MCPServer(vault_path=config.vault_path)

        # Statistics
        self.stats = {
            "files_captured": 0,
            "emails_captured": 0,
            "tasks_processed": 0,
            "approvals_processed": 0,
            "tasks_executed": 0,
            "tasks_completed": 0,
        }

    def step1_capture_files(self) -> int:
        """
        Step 1: Check Inbox/ for new files and create tasks.

        Returns:
            Number of files captured
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Capturing files from Inbox/")
        logger.info("=" * 60)

        try:
            # Run file watcher once (not continuous)
            captured = self.file_watcher.run_once()
            self.stats["files_captured"] = captured
            logger.info(f"Files captured: {captured}")
            return captured
        except Exception as e:
            logger.error(f"Error capturing files: {e}")
            return 0

    def step2_capture_emails(self) -> int:
        """
        Step 2: Check Gmail for new emails and create tasks.

        Returns:
            Number of emails captured
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Capturing emails from Gmail")
        logger.info("=" * 60)

        try:
            # Run gmail watcher once
            captured = self.gmail_watcher.run_once()
            self.stats["emails_captured"] = captured
            logger.info(f"Emails captured: {captured}")
            return captured
        except Exception as e:
            logger.error(f"Error capturing emails: {e}")
            return 0

    def step3_process_tasks(self) -> int:
        """
        Step 3: Process tasks in Needs_Action/ with reasoning skill.

        Returns:
            Number of tasks processed
        """
        logger.info("=" * 60)
        logger.info("STEP 3: Processing tasks with reasoning skill")
        logger.info("=" * 60)

        processed = 0
        pending_tasks = self.task_processor.get_pending_tasks()

        if not pending_tasks:
            logger.info("No pending tasks in Needs_Action/")
            return 0

        logger.info(f"Found {len(pending_tasks)} pending tasks")

        for task_file in pending_tasks:
            try:
                task_id = task_file.stem.replace("task-", "")
                logger.info(f"Processing task: {task_id}")

                # Read task
                task = Task.from_markdown(task_file.read_text(encoding="utf-8"))
                logger.info(f"  Title: {task.title}")
                logger.info(f"  Source: {task.source}")

                # Generate plan
                plan, needs_approval = self.reasoning_skill.generate_plan(task)
                plan_path = self.reasoning_skill.save_plan(plan, task_title=task.title)
                logger.info(f"  Plan: {plan_path.name}")
                logger.info(f"  Needs approval: {needs_approval}")

                if needs_approval:
                    # Create approval request
                    approval_path = self.approval_skill.create_approval_request(task, plan)
                    logger.info(f"  Approval request: {approval_path.name}")
                    logger.info(f"  Status: Awaiting approval")

                    # Move task to Waiting_Approval for tracking
                    waiting_folder = self.vault_path / "Waiting_Approval"
                    dest = waiting_folder / task_file.name
                    task_file.rename(dest)
                    logger.info(f"  Moved to: Waiting_Approval/")
                else:
                    # No approval needed - move to Done
                    done_folder = self.vault_path / "Done"
                    done_folder.mkdir(exist_ok=True)
                    dest = done_folder / task_file.name
                    task_file.rename(dest)
                    logger.info(f"  Status: Completed (no approval needed)")
                    logger.info(f"  Moved to: Done/")
                    self.stats["tasks_completed"] += 1

                processed += 1

            except Exception as e:
                logger.error(f"Error processing task {task_file.name}: {e}")
                continue

        self.stats["tasks_processed"] = processed
        logger.info(f"Tasks processed: {processed}")
        return processed

    def step4_process_approvals(self) -> Dict[str, str]:
        """
        Step 4: Check Waiting_Approval/ for human approvals.

        Returns:
            Dictionary of approval results {task_id: status}
        """
        logger.info("=" * 60)
        logger.info("STEP 4: Processing pending approvals")
        logger.info("=" * 60)

        try:
            results = self.approval_skill.process_pending_approvals()
            self.stats["approvals_processed"] = len(results)

            if not results:
                logger.info("No approvals to process")
            else:
                logger.info(f"Approvals processed: {len(results)}")
                for task_id, status in results.items():
                    logger.info(f"  {task_id}: {status}")

            return results
        except Exception as e:
            logger.error(f"Error processing approvals: {e}")
            return {}

    def step5_execute_approved_tasks(self, approval_results: Dict[str, str]) -> int:
        """
        Step 5: Execute approved tasks via MCP server.

        Args:
            approval_results: Dictionary of approval results from step 4

        Returns:
            Number of tasks executed
        """
        logger.info("=" * 60)
        logger.info("STEP 5: Executing approved tasks via MCP server")
        logger.info("=" * 60)

        executed = 0
        approved_folder = self.vault_path / "Approved"
        waiting_folder = self.vault_path / "Waiting_Approval"

        # Get approved tasks
        approved_tasks = [task_id for task_id, status in approval_results.items() if status == "approved"]

        if not approved_tasks:
            logger.info("No approved tasks to execute")
            return 0

        logger.info(f"Found {len(approved_tasks)} approved tasks")

        for task_id in approved_tasks:
            try:
                # Find task file in Waiting_Approval
                task_file = waiting_folder / f"task-{task_id}.md"

                if not task_file.exists():
                    logger.warning(f"Task file not found: {task_file.name}")
                    continue

                # Read task
                task = Task.from_markdown(task_file.read_text(encoding="utf-8"))
                logger.info(f"Executing task: {task_id}")
                logger.info(f"  Title: {task.title}")

                # Determine action type and execute via MCP server
                action_type = self.reasoning_skill.detect_action_type(task.content)
                logger.info(f"  Action type: {action_type}")

                if action_type == "email":
                    # Extract email details and send
                    entities = self.reasoning_skill.extract_key_entities(task.content)
                    if entities["emails"]:
                        result = self.mcp_server.send_email(
                            to=entities["emails"][0],
                            subject=f"Re: {task.title}",
                            body=task.content,
                        )
                        logger.info(f"  Email result: {result['status']}")
                        if result['status'] == 'success':
                            executed += 1
                    else:
                        logger.warning(f"  No email address found in task")

                elif action_type == "linkedin":
                    # Post to LinkedIn (simulated)
                    result = self.mcp_server.post_linkedin(
                        content=task.content,
                    )
                    logger.info(f"  LinkedIn result: {result['status']}")
                    if result['status'] == 'success':
                        logger.info(f"  Post file: {result['post_file']}")
                        executed += 1

                else:
                    logger.info(f"  Action type '{action_type}' - no MCP execution needed")
                    executed += 1

                # Move task to Done
                done_folder = self.vault_path / "Done"
                done_folder.mkdir(exist_ok=True)
                dest = done_folder / task_file.name
                task_file.rename(dest)
                logger.info(f"  Moved to: Done/")
                self.stats["tasks_completed"] += 1

            except Exception as e:
                logger.error(f"Error executing task {task_id}: {e}")
                continue

        self.stats["tasks_executed"] = executed
        logger.info(f"Tasks executed: {executed}")
        return executed

    def run(self):
        """
        Run complete integrated workflow.
        """
        print("\n" + "=" * 80)
        print("AI EMPLOYEE - SILVER TIER (INTEGRATED RUNNER)")
        print("=" * 80)
        print(f"Vault: {self.vault_path}")
        print("=" * 80 + "\n")

        # Step 1: Capture files
        self.step1_capture_files()

        # Step 2: Capture emails
        self.step2_capture_emails()

        # Step 3: Process tasks
        self.step3_process_tasks()

        # Step 4: Process approvals
        approval_results = self.step4_process_approvals()

        # Step 5: Execute approved tasks
        self.step5_execute_approved_tasks(approval_results)

        # Print summary
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETE - SUMMARY")
        print("=" * 80)
        print(f"Files captured:       {self.stats['files_captured']}")
        print(f"Emails captured:      {self.stats['emails_captured']}")
        print(f"Tasks processed:      {self.stats['tasks_processed']}")
        print(f"Approvals processed:  {self.stats['approvals_processed']}")
        print(f"Tasks executed:       {self.stats['tasks_executed']}")
        print(f"Tasks completed:      {self.stats['tasks_completed']}")
        print("=" * 80 + "\n")


def main():
    """Main entry point for integrated runner"""
    try:
        # Load configuration
        config = Config()

        # Validate vault
        if not config.vault_path.exists():
            print(f"ERROR: Vault not found at {config.vault_path}")
            print("Run: python -m ai_employee init")
            return 1

        # Run integrated workflow
        runner = IntegratedRunner(config)
        runner.run()

        return 0

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
