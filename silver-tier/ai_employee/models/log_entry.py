"""
Log Entry data model

Represents a system action for audit and debugging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class LogEntry:
    """Log entry representing a system action"""

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    action_type: str = ""  # file_detected, task_created, plan_generated, task_moved, error, warning, system_start, system_stop
    task_id: str = "N/A"
    details: str = ""
    outcome: str = "success"  # success, failure, skipped, pending

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "action_type": self.action_type,
            "task_id": self.task_id,
            "details": self.details,
            "outcome": self.outcome,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create LogEntry from dictionary"""
        return cls(
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            action_type=data.get("action_type", ""),
            task_id=data.get("task_id", "N/A"),
            details=data.get("details", ""),
            outcome=data.get("outcome", "success"),
        )

    def to_log_line(self) -> str:
        """Convert to log file format"""
        return f"[{self.timestamp}] {self.action_type.upper()} {self.task_id} {self.details} {self.outcome}"

    @classmethod
    def from_log_line(cls, line: str) -> "LogEntry":
        """Parse LogEntry from log line"""
        # Format: [timestamp] ACTION_TYPE task_id details outcome
        parts = line.strip().split(" ", 4)
        if len(parts) < 5:
            raise ValueError(f"Invalid log line format: {line}")

        timestamp = parts[0].strip("[]")
        action_type = parts[1].lower()
        task_id = parts[2]
        # Split remaining into details and outcome
        remaining = parts[3] + " " + parts[4]
        last_space = remaining.rfind(" ")
        details = remaining[:last_space].strip()
        outcome = remaining[last_space:].strip()

        return cls(
            timestamp=timestamp,
            action_type=action_type,
            task_id=task_id,
            details=details,
            outcome=outcome,
        )
