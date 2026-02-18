"""
Task Processor (Bronze Tier - Claude Code Integration)

This module ONLY detects pending tasks and prepares them for Claude Code processing.
It does NOT generate plans - that's Claude Code's job.
"""

from pathlib import Path
from ai_employee.models.task import Task
from ai_employee.models.log_entry import LogEntry
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class TaskProcessor:
    """Detects pending tasks for Claude Code processing"""

    def __init__(
        self,
        vault_path: Path,
        max_iterations: int = 10,
    ):
        """
        Initialize task processor (Bronze Tier - Claude Code Integration)

        Args:
            vault_path: Path to Obsidian vault
            max_iterations: Maximum tasks to process per cycle

        Note:
            This processor ONLY detects tasks. Claude Code generates plans.
        """
        self.vault_path = vault_path
        self.max_iterations = max_iterations
        self.needs_action_folder = vault_path / "Needs_Action"
        self.activity_log_path = vault_path / "activity.log"

    def get_pending_tasks(self) -> list[Path]:
        """
        Get list of pending task files in /Needs_Action

        Returns:
            List of task file paths, sorted by creation time (oldest first)
        """
        task_files = list(self.needs_action_folder.glob("task-*.md"))

        # Sort by creation time (oldest first)
        task_files.sort(key=lambda f: f.stat().st_ctime)

        return task_files[:self.max_iterations]

    def count_pending_tasks(self) -> int:
        """
        Count pending tasks in /Needs_Action

        Returns:
            Number of pending tasks
        """
        return len(list(self.needs_action_folder.glob("task-*.md")))

    def _log_activity(self, entry: LogEntry) -> None:
        """Write log entry to activity log"""
        try:
            with open(self.activity_log_path, "a", encoding="utf-8") as f:
                f.write(entry.to_log_line() + "\n")
        except Exception as e:
            logger.error(f"Failed to write to activity log: {e}")
