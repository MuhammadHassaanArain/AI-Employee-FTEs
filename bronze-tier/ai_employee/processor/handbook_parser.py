"""
Handbook Parser

Parses Company_Handbook.md and applies rules for plan generation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HandbookRule:
    """Represents a rule from the handbook"""

    title: str
    keywords: List[str]
    action: str  # flag, require_approval, warn, block
    priority: str  # critical, high, medium, low
    rule_text: str


class HandbookParser:
    """Parses and applies handbook rules"""

    def __init__(self, handbook_path: Path):
        """
        Initialize handbook parser

        Args:
            handbook_path: Path to Company_Handbook.md
        """
        self.handbook_path = handbook_path
        self.rules: List[HandbookRule] = []
        self._load_rules()

    def _load_rules(self) -> None:
        """Load and parse rules from handbook"""
        if not self.handbook_path.exists():
            logger.warning(f"Handbook not found: {self.handbook_path}")
            return

        try:
            content = self.handbook_path.read_text(encoding="utf-8")
            self.rules = self._parse_handbook(content)
            logger.info(f"Loaded {len(self.rules)} rules from handbook")
        except Exception as e:
            logger.error(f"Failed to parse handbook: {e}")
            self.rules = []

    def _parse_handbook(self, content: str) -> List[HandbookRule]:
        """
        Parse handbook content into rules

        Args:
            content: Handbook markdown content

        Returns:
            List of HandbookRule objects
        """
        rules = []
        current_priority = None

        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect priority section (## heading)
            if line.startswith("## "):
                priority_text = line[3:].lower()
                if "critical" in priority_text:
                    current_priority = "critical"
                elif "high" in priority_text:
                    current_priority = "high"
                elif "medium" in priority_text:
                    current_priority = "medium"
                elif "low" in priority_text:
                    current_priority = "low"
                i += 1
                continue

            # Detect rule (### heading)
            if line.startswith("### "):
                rule_title = line[4:].strip()
                keywords = []
                action = None
                rule_text_lines = []

                # Parse rule metadata and content
                i += 1
                while i < len(lines) and not lines[i].startswith("#"):
                    line = lines[i].strip()

                    if line.startswith("**Keywords**:"):
                        keywords_str = line.split(":", 1)[1].strip()
                        keywords = [k.strip() for k in keywords_str.split(",")]

                    elif line.startswith("**Action**:"):
                        action = line.split(":", 1)[1].strip()

                    elif line and not line.startswith("**"):
                        rule_text_lines.append(line)

                    i += 1

                # Create rule if valid
                if keywords and action and current_priority:
                    rule = HandbookRule(
                        title=rule_title,
                        keywords=keywords,
                        action=action,
                        priority=current_priority,
                        rule_text=" ".join(rule_text_lines),
                    )
                    rules.append(rule)
                    logger.debug(f"Parsed rule: {rule_title} ({current_priority})")

                continue

            i += 1

        return rules

    def match_rules(self, task_content: str) -> List[HandbookRule]:
        """
        Match rules against task content

        Args:
            task_content: Task content to match against

        Returns:
            List of matched rules
        """
        matched_rules = []
        content_lower = task_content.lower()

        for rule in self.rules:
            # Check if any keyword matches
            for keyword in rule.keywords:
                if keyword.lower() in content_lower:
                    matched_rules.append(rule)
                    logger.debug(f"Matched rule: {rule.title} (keyword: {keyword})")
                    break

        return matched_rules

    def apply_most_restrictive(self, rules: List[HandbookRule]) -> HandbookRule:
        """
        Apply conflict resolution to get most restrictive rule

        Args:
            rules: List of matched rules

        Returns:
            Most restrictive rule
        """
        if not rules:
            return None

        # Priority order: critical > high > medium > low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        # Action precedence: block > require_approval > warn > flag
        action_order = {
            "block": 0,
            "require_approval": 1,
            "warn": 2,
            "flag": 3,
        }

        # Sort by priority first, then by action
        sorted_rules = sorted(
            rules,
            key=lambda r: (
                priority_order.get(r.priority, 99),
                action_order.get(r.action, 99),
            ),
        )

        return sorted_rules[0]

    def get_approval_checkpoints(
        self, rules: List[HandbookRule], steps: List[str]
    ) -> List[int]:
        """
        Determine which steps need approval based on rules

        Args:
            rules: Matched rules
            steps: Plan steps

        Returns:
            List of step indices requiring approval (0-based)
        """
        approval_checkpoints = []

        # Check if any rule requires approval
        for rule in rules:
            if rule.action == "require_approval":
                # Find steps that might trigger this rule
                for i, step in enumerate(steps):
                    step_lower = step.lower()
                    for keyword in rule.keywords:
                        if keyword.lower() in step_lower:
                            if i not in approval_checkpoints:
                                approval_checkpoints.append(i)
                            break

        return sorted(approval_checkpoints)

    def get_warnings(self, rules: List[HandbookRule]) -> List[str]:
        """
        Get warning messages from matched rules

        Args:
            rules: Matched rules

        Returns:
            List of warning messages
        """
        warnings = []

        for rule in rules:
            if rule.action in ["warn", "require_approval", "block"]:
                warnings.append(f"{rule.title}: {rule.rule_text[:200]}")

        return warnings

    def should_block(self, rules: List[HandbookRule]) -> bool:
        """
        Check if any rule blocks plan generation

        Args:
            rules: Matched rules

        Returns:
            True if plan should be blocked
        """
        return any(rule.action == "block" for rule in rules)

    def reload(self) -> None:
        """Reload rules from handbook (for hot-reload)"""
        logger.info("Reloading handbook rules")
        self._load_rules()

    def validate_structure(self) -> bool:
        """
        Validate handbook structure

        Returns:
            True if valid, False otherwise
        """
        if not self.handbook_path.exists():
            logger.error("Handbook file does not exist")
            return False

        try:
            content = self.handbook_path.read_text(encoding="utf-8")

            # Check for required structure
            if not content.startswith("# Company Handbook"):
                logger.error("Handbook must start with '# Company Handbook'")
                return False

            # Check for at least one priority section
            if not re.search(r"## .*(Critical|High|Medium|Low)", content):
                logger.error("Handbook must have at least one priority section")
                return False

            # Check for at least one rule
            if not re.search(r"### ", content):
                logger.error("Handbook must have at least one rule")
                return False

            logger.info("Handbook structure is valid")
            return True

        except Exception as e:
            logger.error(f"Failed to validate handbook: {e}")
            return False

    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get summary of loaded rules

        Returns:
            Dictionary with rule statistics
        """
        return {
            "total_rules": len(self.rules),
            "by_priority": {
                "critical": len([r for r in self.rules if r.priority == "critical"]),
                "high": len([r for r in self.rules if r.priority == "high"]),
                "medium": len([r for r in self.rules if r.priority == "medium"]),
                "low": len([r for r in self.rules if r.priority == "low"]),
            },
            "by_action": {
                "block": len([r for r in self.rules if r.action == "block"]),
                "require_approval": len(
                    [r for r in self.rules if r.action == "require_approval"]
                ),
                "warn": len([r for r in self.rules if r.action == "warn"]),
                "flag": len([r for r in self.rules if r.action == "flag"]),
            },
        }
