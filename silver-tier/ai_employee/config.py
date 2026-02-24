"""
Configuration management for AI Employee (Silver Tier)

Loads configuration from .env file and CLI arguments.
Supports both pattern-based (Bronze) and AI-powered (Silver) modes.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for AI Employee (Silver Tier)"""

    def __init__(
        self,
        vault_path: str = None,
        watch_folder: str = None,
        max_iterations: int = None,
        log_level: str = None,
        anthropic_api_key: str = None,
        claude_model: str = None,
    ):
        """
        Initialize configuration

        Args:
            vault_path: Path to Obsidian vault (overrides .env)
            watch_folder: Folder to monitor (overrides .env)
            max_iterations: Max tasks per cycle (overrides .env)
            log_level: Logging level (overrides .env)
            anthropic_api_key: Anthropic API key for Claude (overrides .env)
            claude_model: Claude model to use (overrides .env)
        """
        # Load .env file
        load_dotenv()

        # Paths and behavior
        self.vault_path = Path(
            vault_path or os.getenv("VAULT_PATH", "./ai_employee_vault")
        )

        # Default watch folder is Inbox inside vault
        default_watch = str(self.vault_path / "Inbox")
        self.watch_folder = Path(
            watch_folder or os.getenv("WATCH_FOLDER", default_watch)
        )

        self.max_iterations = (
            max_iterations or int(os.getenv("MAX_ITERATIONS", "10"))
        )

        self.poll_interval = int(os.getenv("POLL_INTERVAL", "60"))

        self.log_level = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()

        # Silver Tier: AI configuration
        self.anthropic_api_key = (
            anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        )

        self.claude_model = (
            claude_model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
        )

        self.claude_max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))

        # Mode selection
        self.use_ai_reasoning = os.getenv("USE_AI_REASONING", "false").lower() == "true"

        # LinkedIn Configuration
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.linkedin_redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")

    def validate(self):
        """Validate configuration"""
        if self.max_iterations < 1:
            raise ValueError("MAX_ITERATIONS must be at least 1")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")

        # Validate AI configuration if AI reasoning is enabled
        if self.use_ai_reasoning and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when USE_AI_REASONING=true"
            )

        return True

    def is_ai_mode(self) -> bool:
        """Check if AI reasoning mode is enabled"""
        return self.use_ai_reasoning and bool(self.anthropic_api_key)
