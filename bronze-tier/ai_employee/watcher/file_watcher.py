"""
File Watcher

Monitors a folder for new files using watchdog library.
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from ai_employee.watcher.task_creator import TaskCreator
from ai_employee.utils.file_tracker import FileTracker
from ai_employee.vault.dashboard import DashboardUpdater
from ai_employee.models.log_entry import LogEntry
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class TaskFileHandler(FileSystemEventHandler):
    """Handles file system events for task creation"""

    def __init__(
        self,
        task_creator: TaskCreator,
        file_tracker: FileTracker,
        dashboard_updater: DashboardUpdater,
        activity_log_path: Path,
    ):
        """
        Initialize file handler

        Args:
            task_creator: TaskCreator instance
            file_tracker: FileTracker instance
            dashboard_updater: DashboardUpdater instance
            activity_log_path: Path to activity log file
        """
        super().__init__()
        self.task_creator = task_creator
        self.file_tracker = file_tracker
        self.dashboard_updater = dashboard_updater
        self.activity_log_path = activity_log_path

    def _is_file_stable(self, file_path: Path, wait_time: float = 0.5, max_attempts: int = 10) -> bool:
        """
        Check if file is stable (fully written) by monitoring size changes.

        Args:
            file_path: Path to file
            wait_time: Time to wait between checks (seconds)
            max_attempts: Maximum number of attempts

        Returns:
            True if file is stable, False otherwise
        """
        if not file_path.exists():
            return False

        try:
            previous_size = -1
            for attempt in range(max_attempts):
                current_size = file_path.stat().st_size

                # File size hasn't changed, it's stable
                if current_size == previous_size and current_size > 0:
                    return True

                previous_size = current_size
                time.sleep(wait_time)

            # File still changing after max attempts, but proceed anyway
            logger.warning(f"File {file_path.name} still changing after {max_attempts} attempts")
            return True

        except Exception as e:
            logger.error(f"Error checking file stability: {e}")
            return False

    def _should_process_file(self, file_path: Path) -> bool:
        """
        Check if file should be processed.

        Args:
            file_path: Path to file

        Returns:
            True if file should be processed, False otherwise
        """
        # Ignore directories
        if file_path.is_dir():
            return False

        # Ignore hidden files and temp files
        if file_path.name.startswith(".") or file_path.name.endswith((".tmp", ".swp", "~")):
            logger.debug(f"Ignoring file: {file_path}")
            return False

        # Check if already processed
        if self.file_tracker.is_processed(str(file_path.absolute())):
            logger.debug(f"File already processed: {file_path}")
            return False

        return True

    def _process_file(self, file_path: Path):
        """
        Process a detected file and create a task.

        Args:
            file_path: Path to file to process
        """
        logger.info(f"New file detected: {file_path}")

        # Wait for file to be fully written
        if not self._is_file_stable(file_path):
            logger.warning(f"File not stable, skipping: {file_path}")
            return

        try:
            # Log file detection
            self._log_activity(
                LogEntry(
                    action_type="file_detected",
                    details=f"Detected new file: {file_path.name}",
                    outcome="success",
                )
            )

            # Create task
            task = self.task_creator.create_task_from_file(file_path)

            # Mark as processed
            self.file_tracker.mark_processed(str(file_path.absolute()))

            # Log task creation
            self._log_activity(
                LogEntry(
                    action_type="task_created",
                    task_id=task.id,
                    details=f"Created task: {task.title}",
                    outcome="success",
                )
            )

            # Update dashboard
            self.dashboard_updater.increment_needs_action()
            self.dashboard_updater.add_activity(
                f"Created task from {file_path.name}"
            )

            logger.success(f"Successfully created task {task.id} from {file_path}")

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")

            # Log error
            self._log_activity(
                LogEntry(
                    action_type="error",
                    details=f"Failed to process {file_path.name}: {str(e)}",
                    outcome="failure",
                )
            )

    def on_created(self, event: FileCreatedEvent):
        """
        Handle file creation event

        Args:
            event: File creation event
        """
        # Ignore directories
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if should process
        if not self._should_process_file(file_path):
            return

        # Process the file
        self._process_file(file_path)

    def on_modified(self, event: FileModifiedEvent):
        """
        Handle file modification event (catches pasted files on Windows)

        Args:
            event: File modification event
        """
        # Ignore directories
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if should process
        if not self._should_process_file(file_path):
            return

        # Process the file (this catches pasted files)
        self._process_file(file_path)

    def _log_activity(self, entry: LogEntry):
        """Write log entry to activity log"""
        try:
            with open(self.activity_log_path, "a", encoding="utf-8") as f:
                f.write(entry.to_log_line() + "\n")
        except Exception as e:
            logger.error(f"Failed to write to activity log: {e}")


class FileWatcher:
    """Watches a folder for new files"""

    def __init__(
        self,
        watch_folder: Path,
        vault_path: Path,
    ):
        """
        Initialize file watcher

        Args:
            watch_folder: Folder to monitor
            vault_path: Path to Obsidian vault
        """
        self.watch_folder = watch_folder
        self.vault_path = vault_path

        # Initialize components
        self.task_creator = TaskCreator(vault_path)
        self.file_tracker = FileTracker(vault_path / ".file_tracker.json")
        self.dashboard_updater = DashboardUpdater(vault_path)
        self.activity_log_path = vault_path / "activity.log"

        # Create event handler
        self.event_handler = TaskFileHandler(
            self.task_creator,
            self.file_tracker,
            self.dashboard_updater,
            self.activity_log_path,
        )

        # Create observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.watch_folder),
            recursive=False,
        )

    def start(self):
        """Start watching for files"""
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting file watcher on: {self.watch_folder}")
        self.observer.start()

        # Log system start
        entry = LogEntry(
            action_type="system_start",
            details=f"Started watching {self.watch_folder}",
            outcome="success",
        )
        with open(self.activity_log_path, "a", encoding="utf-8") as f:
            f.write(entry.to_log_line() + "\n")

    def stop(self):
        """Stop watching for files"""
        logger.info("Stopping file watcher")
        self.observer.stop()
        self.observer.join()

        # Log system stop
        entry = LogEntry(
            action_type="system_stop",
            details="Stopped file watcher",
            outcome="success",
        )
        with open(self.activity_log_path, "a", encoding="utf-8") as f:
            f.write(entry.to_log_line() + "\n")

    def is_alive(self) -> bool:
        """Check if watcher is running"""
        return self.observer.is_alive()
