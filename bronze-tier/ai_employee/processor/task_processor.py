"""
Task Processor

Processes tasks from /Needs_Action and generates plans.
"""

from pathlib import Path
from ai_employee.models.task import Task
from ai_employee.models.plan import Plan
from ai_employee.models.log_entry import LogEntry
from ai_employee.watcher.task_creator import TaskCreator
from ai_employee.processor.claude_client import ClaudeClient
from ai_employee.processor.handbook_parser import HandbookParser
from ai_employee.vault.dashboard import DashboardUpdater
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class TaskProcessor:
    """Processes tasks and generates plans"""

    def __init__(
        self,
        vault_path: Path,
        api_key: str,
        max_iterations: int = 10,
    ):
        """
        Initialize task processor

        Args:
            vault_path: Path to Obsidian vault
            api_key: Anthropic API key
            max_iterations: Maximum tasks to process per cycle
        """
        self.vault_path = vault_path
        self.max_iterations = max_iterations
        self.needs_action_folder = vault_path / "Needs_Action"
        self.plans_folder = vault_path / "Plans"
        self.activity_log_path = vault_path / "activity.log"

        # Initialize components
        self.task_creator = TaskCreator(vault_path)
        self.handbook_parser = HandbookParser(vault_path / "Company_Handbook.md")
        self.claude_client = ClaudeClient(api_key, self.handbook_parser)
        self.dashboard_updater = DashboardUpdater(vault_path)

    def process_tasks(self) -> int:
        """
        Process all tasks in /Needs_Action

        Returns:
            Number of tasks processed
        """
        logger.info("Starting task processing cycle")

        # Get all task files
        task_files = list(self.needs_action_folder.glob("task-*.md"))

        if not task_files:
            logger.info("No tasks to process")
            return 0

        # Limit to max iterations
        tasks_to_process = task_files[: self.max_iterations]
        logger.info(f"Processing {len(tasks_to_process)} tasks (max: {self.max_iterations})")

        processed_count = 0

        for task_file in tasks_to_process:
            try:
                # Load task
                task = self._load_task(task_file)

                # Update status to processing
                task.status = "processing"
                self._save_task(task, task_file)

                # Generate plan
                plan = self.claude_client.generate_plan(task)

                # Save plan
                self._save_plan(plan, task.title)

                # Move task to Done
                self.task_creator.move_task_to_done(task.id)

                # Log success
                self._log_activity(
                    LogEntry(
                        action_type="plan_generated",
                        task_id=task.id,
                        details=f"Generated plan with {len(plan.steps)} steps",
                        outcome="success",
                    )
                )

                self._log_activity(
                    LogEntry(
                        action_type="task_moved",
                        task_id=task.id,
                        details=f"Moved task to Done",
                        outcome="success",
                    )
                )

                # Update dashboard
                self.dashboard_updater.decrement_needs_action()
                self.dashboard_updater.increment_done()

                processed_count += 1
                logger.info(f"Successfully processed task {task.id}")

            except Exception as e:
                logger.error(f"Failed to process task {task_file.name}: {e}")

                # Log error
                self._log_activity(
                    LogEntry(
                        action_type="error",
                        task_id=task_file.stem.replace("task-", ""),
                        details=f"Failed to process: {str(e)}",
                        outcome="failure",
                    )
                )

                # Update task status to error
                try:
                    task = self._load_task(task_file)
                    task.status = "error"
                    task.error_message = str(e)
                    self._save_task(task, task_file)
                except Exception as save_error:
                    logger.error(f"Failed to update task status: {save_error}")

        logger.info(f"Processing cycle complete: {processed_count} tasks processed")
        return processed_count

    def _load_task(self, task_file: Path) -> Task:
        """Load task from file"""
        content = task_file.read_text(encoding="utf-8")
        return Task.from_markdown(content)

    def _save_task(self, task: Task, task_file: Path) -> None:
        """Save task to file"""
        task_file.write_text(task.to_markdown(), encoding="utf-8")

    def _save_plan(self, plan: Plan, task_title: str) -> None:
        """
        Save plan to /Plans folder

        Args:
            plan: Plan object
            task_title: Title of the task (for plan heading)
        """
        plan_file = self.plans_folder / f"plan-{plan.task_id}.md"
        plan_content = plan.to_markdown(task_title)
        plan_file.write_text(plan_content, encoding="utf-8")
        logger.info(f"Saved plan to: {plan_file}")

    def _log_activity(self, entry: LogEntry) -> None:
        """Write log entry to activity log"""
        try:
            with open(self.activity_log_path, "a", encoding="utf-8") as f:
                f.write(entry.to_log_line() + "\n")
        except Exception as e:
            logger.error(f"Failed to write to activity log: {e}")

    def run_loop(self) -> None:
        """
        Run processing loop until queue is empty or max iterations reached

        This is for Phase 6: User Story 3 - Autonomous Processing Loop
        """
        logger.info("Starting autonomous processing loop")

        iteration = 0
        while iteration < self.max_iterations:
            # Check if there are tasks to process
            task_files = list(self.needs_action_folder.glob("task-*.md"))

            if not task_files:
                logger.info("Queue empty, stopping loop")
                self._log_activity(
                    LogEntry(
                        action_type="system_stop",
                        details="Processing loop completed: queue empty",
                        outcome="success",
                    )
                )
                break

            # Process tasks
            processed = self.process_tasks()

            if processed == 0:
                logger.warning("No tasks processed, stopping loop")
                break

            iteration += 1

        if iteration >= self.max_iterations:
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            self._log_activity(
                LogEntry(
                    action_type="warning",
                    details=f"Max iterations ({self.max_iterations}) reached",
                    outcome="skipped",
                )
            )

        logger.info(f"Processing loop complete: {iteration} iterations")
