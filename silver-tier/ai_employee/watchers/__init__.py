"""
File watching and task creation (Silver Tier)

Multiple watchers for different input sources:
- FileWatcher: Monitor local file system (Bronze Tier)
- GmailWatcher: Monitor Gmail inbox (Silver Tier)
"""

from ai_employee.watchers.file_watcher import FileWatcher
from ai_employee.watchers.gmail_watcher import GmailWatcher
from ai_employee.watchers.task_creator import TaskCreator

__all__ = [
    "FileWatcher",
    "GmailWatcher",
    "TaskCreator",
]
