"""
Task Creator

Converts detected files into markdown tasks with YAML frontmatter.
"""

from pathlib import Path
from datetime import datetime
from ai_employee.models.task import Task
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class TaskCreator:
    """Creates task files from detected files"""

    def __init__(self, vault_path: Path):
        """
        Initialize task creator

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = vault_path
        self.needs_action_folder = vault_path / "Needs_Action"

    def create_task_from_file(self, file_path: Path) -> Task:
        """
        Create task from detected file

        Args:
            file_path: Path to detected file

        Returns:
            Created Task object

        Raises:
            Exception if file cannot be read or task cannot be created
        """
        logger.info(f"Creating task from file: {file_path}")

        # Read file content
        try:
            content = self._read_file_content(file_path)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

        # Extract title from filename or first line
        title = self._extract_title(file_path, content)

        # Create Task object
        task = Task(
            title=title,
            content=content,
            source_path=str(file_path.absolute()),
            original_filename=file_path.name,
            file_size=file_path.stat().st_size,
            detected_at=datetime.utcnow().isoformat() + "Z",
            status="needs_action",
        )

        # Save task to vault
        task_file_path = self.needs_action_folder / f"task-{task.id}.md"
        try:
            task_file_path.write_text(task.to_markdown(), encoding="utf-8")
            logger.info(f"Created task file: {task_file_path}")
        except Exception as e:
            logger.error(f"Failed to write task file: {e}")
            raise

        return task

    def _read_file_content(self, file_path: Path) -> str:
        """
        Read file content with encoding detection

        Args:
            file_path: Path to file

        Returns:
            File content as string
        """
        # Try UTF-8 first
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            try:
                return file_path.read_text(encoding="latin-1")
            except Exception as e:
                logger.warning(f"Failed to decode file with latin-1: {e}")
                # Last resort: read as binary and represent as hex
                binary_content = file_path.read_bytes()
                return f"[Binary file - {len(binary_content)} bytes]\n\nUnable to decode as text."

    def _extract_title(self, file_path: Path, content: str) -> str:
        """
        Extract title from filename or content

        Args:
            file_path: Path to file
            content: File content

        Returns:
            Extracted title
        """
        # Try to use first non-empty line as title
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Use first line, truncate if too long
                title = line[:200] if len(line) > 200 else line
                return title

        # Fallback to filename without extension
        return file_path.stem.replace("_", " ").replace("-", " ").title()

    def load_task(self, task_id: str) -> Task:
        """
        Load task from vault

        Args:
            task_id: Task ID

        Returns:
            Task object

        Raises:
            FileNotFoundError if task file doesn't exist
        """
        task_file = self.needs_action_folder / f"task-{task_id}.md"
        if not task_file.exists():
            # Check in Done folder
            task_file = self.vault_path / "Done" / f"task-{task_id}.md"
            if not task_file.exists():
                raise FileNotFoundError(f"Task not found: {task_id}")

        content = task_file.read_text(encoding="utf-8")
        return Task.from_markdown(content)

    def move_task_to_done(self, task_id: str) -> None:
        """
        Move task from Needs_Action to Done

        Args:
            task_id: Task ID
        """
        source = self.needs_action_folder / f"task-{task_id}.md"
        dest = self.vault_path / "Done" / f"task-{task_id}.md"

        if not source.exists():
            logger.warning(f"Task file not found: {source}")
            return

        # Update task status
        task = Task.from_markdown(source.read_text(encoding="utf-8"))
        task.status = "done"

        # Write to Done folder
        dest.write_text(task.to_markdown(), encoding="utf-8")

        # Remove from Needs_Action
        source.unlink()

        logger.info(f"Moved task {task_id} to Done")
