"""
Configuration management for AI Employee

Loads configuration from .env file and CLI arguments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for AI Employee"""

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
        """
        # Load .env file
        load_dotenv()

        # Required: API key
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in .env file or environment variables."
            )

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
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        if self.max_iterations < 1:
            raise ValueError("MAX_ITERATIONS must be at least 1")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")

        return True
