"""
File Tracker

Tracks processed files to prevent duplicate task creation.
"""

import json
from pathlib import Path
from typing import Set
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class FileTracker:
    """Tracks processed files using JSON storage"""

    def __init__(self, tracker_file: Path):
        """
        Initialize file tracker

        Args:
            tracker_file: Path to JSON file storing processed files
        """
        self.tracker_file = tracker_file
        self.processed_files: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """Load processed files from JSON"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_files = set(data.get("processed_files", []))
                logger.info(f"Loaded {len(self.processed_files)} processed files")
            except Exception as e:
                logger.error(f"Failed to load tracker file: {e}")
                self.processed_files = set()
        else:
            logger.info("No existing tracker file, starting fresh")

    def _save(self) -> None:
        """Save processed files to JSON"""
        try:
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"processed_files": list(self.processed_files)},
                    f,
                    indent=2,
                )
            logger.debug(f"Saved {len(self.processed_files)} processed files")
        except Exception as e:
            logger.error(f"Failed to save tracker file: {e}")

    def is_processed(self, file_path: str) -> bool:
        """
        Check if file has been processed

        Args:
            file_path: Absolute path to file

        Returns:
            True if already processed, False otherwise
        """
        return file_path in self.processed_files

    def mark_processed(self, file_path: str) -> None:
        """
        Mark file as processed

        Args:
            file_path: Absolute path to file
        """
        self.processed_files.add(file_path)
        self._save()
        logger.debug(f"Marked as processed: {file_path}")

    def unmark_processed(self, file_path: str) -> None:
        """
        Unmark file as processed (for retry scenarios)

        Args:
            file_path: Absolute path to file
        """
        if file_path in self.processed_files:
            self.processed_files.remove(file_path)
            self._save()
            logger.debug(f"Unmarked as processed: {file_path}")

    def get_processed_count(self) -> int:
        """Get count of processed files"""
        return len(self.processed_files)

    def clear(self) -> None:
        """Clear all processed files (use with caution)"""
        self.processed_files.clear()
        self._save()
        logger.warning("Cleared all processed files")
