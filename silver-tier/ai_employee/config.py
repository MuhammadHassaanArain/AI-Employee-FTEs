"""
Configuration management for AI Employee (Bronze Tier - Local Only)

Loads configuration from .env file and CLI arguments.
No API keys required - all processing is done locally.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for AI Employee (Bronze Tier)"""

    def __init__(
        self,
        vault_path: str = None,
        watch_folder: str = None,
        max_iterations: int = None,
        log_level: str = None,
    ):
        """
        Initialize configuration

        Args:
            vault_path: Path to Obsidian vault (overrides .env)
            watch_folder: Folder to monitor (overrides .env)
            max_iterations: Max tasks per cycle (overrides .env)
            log_level: Logging level (overrides .env)

        Note:
            Bronze Tier operates locally without any API keys.
            All task processing is done using rule-based logic.
        """
        # Load .env file (optional for Bronze Tier)
        load_dotenv()

        # Optional: Paths and behavior
        self.vault_path = Path(
            vault_path or os.getenv("VAULT_PATH", "./ai_employee_vault")
        )

        # Default watch folder is Inbox inside vault
        default_watch = str(self.vault_path / "Inbox")
        self.watch_folder = Path(
            watch_folder or os.getenv("WATCH_FOLDER", default_watch)
        )

        self.max_iterations = (
            max_iterations
            or int(os.getenv("MAX_ITERATIONS", "10"))
        )

        self.poll_interval = int(os.getenv("POLL_INTERVAL", "60"))

        self.log_level = (
            log_level or os.getenv("LOG_LEVEL", "INFO")
        ).upper()

    def validate(self):
        """Validate configuration"""
        if self.max_iterations < 1:
            raise ValueError("MAX_ITERATIONS must be at least 1")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")

        return True
