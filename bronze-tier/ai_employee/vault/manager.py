"""
Vault Manager

Manages Obsidian vault structure and initialization.
"""

from pathlib import Path
from typing import Dict
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class VaultManager:
    """Manages Obsidian vault structure"""

    def __init__(self, vault_path: str):
        """
        Initialize vault manager

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.folders = {
            "inbox": self.vault_path / "Inbox",
            "needs_action": self.vault_path / "Needs_Action",
            "done": self.vault_path / "Done",
            "plans": self.vault_path / "Plans",
        }

    def create_vault(self) -> None:
        """Create vault structure with all required folders and files"""
        logger.info(f"Creating vault at: {self.vault_path}")

        # Create vault root
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Create folders
        for folder_name, folder_path in self.folders.items():
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_name} at {folder_path}")

        # Create Dashboard.md
        dashboard_path = self.vault_path / "Dashboard.md"
        if not dashboard_path.exists():
            dashboard_content = self._get_default_dashboard()
            dashboard_path.write_text(dashboard_content, encoding="utf-8")
            logger.info(f"Created Dashboard.md")

        # Create Company_Handbook.md
        handbook_path = self.vault_path / "Company_Handbook.md"
        if not handbook_path.exists():
            handbook_content = self._get_default_handbook()
            handbook_path.write_text(handbook_content, encoding="utf-8")
            logger.info(f"Created Company_Handbook.md")

        # Create activity.log
        log_path = self.vault_path / "activity.log"
        if not log_path.exists():
            log_path.write_text("", encoding="utf-8")
            logger.info(f"Created activity.log")

        logger.info("Vault creation complete")

    def validate_structure(self) -> bool:
        """
        Validate vault structure exists

        Returns:
            True if valid, False otherwise
        """
        if not self.vault_path.exists():
            logger.error(f"Vault path does not exist: {self.vault_path}")
            return False

        # Check required folders
        for folder_name, folder_path in self.folders.items():
            if not folder_path.exists():
                logger.warning(f"Missing folder: {folder_name} at {folder_path}")
                # Auto-repair: create missing folder
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Auto-repaired: created {folder_name}")

        # Check required files
        dashboard_path = self.vault_path / "Dashboard.md"
        if not dashboard_path.exists():
            logger.warning("Missing Dashboard.md")
            dashboard_path.write_text(self._get_default_dashboard(), encoding="utf-8")
            logger.info("Auto-repaired: created Dashboard.md")

        handbook_path = self.vault_path / "Company_Handbook.md"
        if not handbook_path.exists():
            logger.warning("Missing Company_Handbook.md")
            handbook_path.write_text(self._get_default_handbook(), encoding="utf-8")
            logger.info("Auto-repaired: created Company_Handbook.md")

        return True

    def get_paths(self) -> Dict[str, Path]:
        """
        Get all vault paths

        Returns:
            Dictionary of path names to Path objects
        """
        return {
            "vault": self.vault_path,
            "inbox": self.folders["inbox"],
            "needs_action": self.folders["needs_action"],
            "done": self.folders["done"],
            "plans": self.folders["plans"],
            "dashboard": self.vault_path / "Dashboard.md",
            "handbook": self.vault_path / "Company_Handbook.md",
            "activity_log": self.vault_path / "activity.log",
        }

    def _get_default_dashboard(self) -> str:
        """Get default Dashboard.md content"""
        from datetime import datetime

        return f"""# AI Employee Dashboard

**Last Updated**: {datetime.utcnow().isoformat()}Z
**System Status**: Idle

## Task Counts

- **Needs Action**: 0 tasks
- **In Progress**: 0 tasks
- **Completed Today**: 0 tasks
- **Total Completed**: 0 tasks
- **Errors**: 0 tasks

## Recent Activity (Last 10 Actions)

_No activity yet_

## System Configuration

- **Monitored Folder**: Not configured
- **Vault Path**: {self.vault_path}
- **Max Iterations**: 10
- **Claude Model**: claude-3-5-sonnet-20241022

## Quick Links

- [[Company_Handbook]]
- [[Needs_Action/]]
- [[Plans/]]
- [[Done/]]
"""

    def _get_default_handbook(self) -> str:
        """Get default Company_Handbook.md content"""
        return """# Company Handbook

## Critical Rules

### Human approval required for payments >$50
**Keywords**: payment, transfer, invoice, $, money
**Action**: require_approval

Any task involving financial transactions over $50 must include an explicit approval checkpoint before execution.

### Never share sensitive data externally
**Keywords**: password, API key, token, credential, secret
**Action**: block

Tasks must not include steps that transmit sensitive information outside the local system.

## High Priority Rules

### Always flag urgent emails
**Keywords**: urgent, ASAP, immediate, critical
**Action**: flag

Tasks containing urgent keywords should be highlighted in the plan for immediate attention.

## Medium Priority Rules

### Log all external communications
**Keywords**: email, send, message, notify
**Action**: warn

Tasks involving external communications should include a logging step to maintain an audit trail.
"""
