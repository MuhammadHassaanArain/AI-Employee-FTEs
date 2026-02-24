"""
Plan data model (Updated for Claude Reasoning Skill)

Represents an AI-generated action plan for a task.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import uuid


@dataclass
class Plan:
    """Plan entity representing an action plan"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    task_title: str = ""
    task_source: str = ""
    action_type: str = "unknown"
    entities: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    approval_required: bool = False
    approval_checkpoints: List[int] = field(default_factory=list)
    handbook_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reasoning: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    model_used: str = "claude-sonnet-4-6"
    generation_time_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML frontmatter"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "task_source": self.task_source,
            "action_type": self.action_type,
            "approval_required": self.approval_required,
            "created_at": self.created_at,
            "handbook_rules": self.handbook_rules,
            "approval_checkpoints": self.approval_checkpoints,
            "model_used": self.model_used,
            "generation_time_ms": self.generation_time_ms,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plan":
        """Create Plan from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            task_id=data.get("task_id", ""),
            task_title=data.get("task_title", ""),
            task_source=data.get("task_source", ""),
            action_type=data.get("action_type", "unknown"),
            entities=data.get("entities", []),
            steps=data.get("steps", []),
            approval_required=data.get("approval_required", False),
            approval_checkpoints=data.get("approval_checkpoints", []),
            handbook_rules=data.get("handbook_rules", []),
            warnings=data.get("warnings", []),
            reasoning=data.get("reasoning", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            model_used=data.get("model_used", "claude-sonnet-4-6"),
            generation_time_ms=data.get("generation_time_ms", 0),
        )

    def to_markdown(self) -> str:
        """Convert to markdown format with YAML frontmatter"""
        import frontmatter

        # Build content
        content_lines = [
            f"# Action Plan: {self.task_title}",
            "",
            f"**Task ID**: {self.task_id}",
            f"**Task Source**: {self.task_source}",
            f"**Action Type**: {self.action_type}",
            f"**Approval Required**: {self.approval_required}",
            f"**Generated**: {self.created_at}",
            f"**Model**: {self.model_used}",
            "",
        ]

        # Add entities if present
        if self.entities:
            content_lines.extend([
                "## Extracted Entities",
                "",
            ])
            for entity in self.entities:
                content_lines.append(f"- {entity}")
            content_lines.append("")

        # Add steps
        content_lines.extend([
            "## Action Steps",
            "",
        ])

        for i, step in enumerate(self.steps):
            step_num = i + 1
            if i in self.approval_checkpoints:
                content_lines.append(f"{step_num}. **[APPROVAL REQUIRED]** {step}")
            else:
                content_lines.append(f"{step_num}. {step}")

        # Add handbook rules
        if self.handbook_rules:
            content_lines.extend([
                "",
                "## Handbook Rules Applied",
                "",
            ])
            for rule in self.handbook_rules:
                content_lines.append(f"- {rule}")

        # Add warnings
        if self.warnings:
            content_lines.extend([
                "",
                "## Warnings",
                "",
            ])
            for warning in self.warnings:
                content_lines.append(f"⚠️ {warning}")

        # Add reasoning
        if self.reasoning:
            content_lines.extend([
                "",
                "## Reasoning",
                "",
                self.reasoning,
            ])

        content = "\n".join(content_lines)
        post = frontmatter.Post(content, **self.to_dict())
        return frontmatter.dumps(post)

    @classmethod
    def from_markdown(cls, content: str) -> "Plan":
        """Create Plan from markdown with YAML frontmatter"""
        import frontmatter

        post = frontmatter.loads(content)
        plan = cls.from_dict(post.metadata)

        # Parse steps from content
        lines = post.content.split("\n")
        in_steps = False
        steps = []

        for line in lines:
            if line.strip() == "## Action Steps":
                in_steps = True
                continue
            elif line.startswith("## "):
                in_steps = False

            if in_steps and line.strip() and line[0].isdigit():
                # Extract step text (remove number and approval marker)
                step_text = line.split(".", 1)[1].strip()
                step_text = step_text.replace("**[APPROVAL REQUIRED]**", "").strip()
                steps.append(step_text)

        plan.steps = steps
        return plan
