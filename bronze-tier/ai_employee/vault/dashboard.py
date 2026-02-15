"""
Dashboard Updater

Updates Dashboard.md with task counts and recent activity.
"""

from pathlib import Path
from datetime import datetime
from typing import List
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class DashboardUpdater:
    """Updates Obsidian dashboard with system status"""

    def __init__(self, vault_path: Path):
        """
        Initialize dashboard updater

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = vault_path
        self.dashboard_path = vault_path / "Dashboard.md"
        self.needs_action_folder = vault_path / "Needs_Action"
        self.done_folder = vault_path / "Done"
        self.activity_log_path = vault_path / "activity.log"

    def update_dashboard(self):
        """Update dashboard with current counts and activity"""
        try:
            # Get counts
            needs_action_count = self._count_tasks(self.needs_action_folder)
            done_count = self._count_tasks(self.done_folder)
            recent_activity = self._get_recent_activity(limit=10)

            # Build dashboard content
            content = self._build_dashboard_content(
                needs_action_count,
                done_count,
                recent_activity,
            )

            # Write to file
            self.dashboard_path.write_text(content, encoding="utf-8")
            logger.debug("Dashboard updated")

        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")

    def increment_needs_action(self):
        """Increment Needs Action count"""
        self.update_dashboard()

    def decrement_needs_action(self):
        """Decrement Needs Action count"""
        self.update_dashboard()

    def increment_done(self):
        """Increment Done count"""
        self.update_dashboard()

    def add_activity(self, message: str):
        """
        Add activity entry to dashboard

        Args:
            message: Activity message
        """
        self.update_dashboard()

    def _count_tasks(self, folder: Path) -> int:
        """Count task files in folder"""
        if not folder.exists():
            return 0
        return len(list(folder.glob("task-*.md")))

    def _get_recent_activity(self, limit: int = 10) -> List[str]:
        """
        Get recent activity from log

        Args:
            limit: Maximum number of entries

        Returns:
            List of activity strings
        """
        if not self.activity_log_path.exists():
            return []

        try:
            with open(self.activity_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Get last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines

            # Format for display
            activities = []
            for line in reversed(recent_lines):
                line = line.strip()
                if line:
                    activities.append(line)

            return activities

        except Exception as e:
            logger.error(f"Failed to read activity log: {e}")
            return []

    def _build_dashboard_content(
        self,
        needs_action_count: int,
        done_count: int,
        recent_activity: List[str],
    ) -> str:
        """Build dashboard markdown content"""
        timestamp = datetime.utcnow().isoformat() + "Z"

        content = f"""# AI Employee Dashboard

**Last Updated**: {timestamp}
**System Status**: Running

## Task Counts

- **Needs Action**: {needs_action_count} tasks
- **In Progress**: 0 tasks
- **Completed Today**: {done_count} tasks
- **Total Completed**: {done_count} tasks
- **Errors**: 0 tasks

## Recent Activity (Last 10 Actions)

"""

        if recent_activity:
            for i, activity in enumerate(recent_activity, 1):
                content += f"{i}. {activity}\n"
        else:
            content += "_No activity yet_\n"

        content += f"""
## System Configuration

- **Monitored Folder**: {self.vault_path.parent / "monitored"}
- **Vault Path**: {self.vault_path}
- **Max Iterations**: 10
- **Claude Model**: claude-3-5-sonnet-20241022

## Quick Links

- [[Company_Handbook]]
- [[Needs_Action/]]
- [[Plans/]]
- [[Done/]]
"""

        return content
