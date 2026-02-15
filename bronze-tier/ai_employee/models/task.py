"""
Task data model

Represents a work item captured from the monitored source.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
import uuid


@dataclass
class Task:
    """Task entity representing a work item"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    source_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = "needs_action"  # needs_action, processing, done, error
    original_filename: str = ""
    file_size: int = 0
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML frontmatter"""
        data = {
            "id": self.id,
            "title": self.title,
            "source_path": self.source_path,
            "created_at": self.created_at,
            "status": self.status,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "detected_at": self.detected_at,
        }
        if self.error_message:
            data["error_message"] = self.error_message
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            source_path=data.get("source_path", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            status=data.get("status", "needs_action"),
            original_filename=data.get("original_filename", ""),
            file_size=data.get("file_size", 0),
            detected_at=data.get("detected_at", datetime.utcnow().isoformat() + "Z"),
            error_message=data.get("error_message", ""),
        )

    def to_markdown(self) -> str:
        """Convert to markdown format with YAML frontmatter"""
        import frontmatter

        post = frontmatter.Post(self.content, **self.to_dict())
        return frontmatter.dumps(post)

    @classmethod
    def from_markdown(cls, content: str) -> "Task":
        """Create Task from markdown with YAML frontmatter"""
        import frontmatter

        post = frontmatter.loads(content)
        task = cls.from_dict(post.metadata)
        task.content = post.content
        return task
