"""
Claude Client

Integrates with Claude API for plan generation.
"""

import time
from pathlib import Path
from typing import Dict, Any, List
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from ai_employee.models.task import Task
from ai_employee.models.plan import Plan
from ai_employee.processor.handbook_parser import HandbookParser
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """Client for Claude API integration"""

    def __init__(self, api_key: str, handbook_parser: HandbookParser):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key
            handbook_parser: HandbookParser instance
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.handbook_parser = handbook_parser
        self.model = "claude-3-5-sonnet-20241022"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def generate_plan(self, task: Task) -> Plan:
        """
        Generate action plan for task using Claude

        Args:
            task: Task to generate plan for

        Returns:
            Generated Plan object

        Raises:
            Exception if plan generation fails after retries
        """
        logger.info(f"Generating plan for task: {task.id}")
        start_time = time.time()

        try:
            # Match handbook rules
            matched_rules = self.handbook_parser.match_rules(
                task.title + "\n" + task.content
            )

            # Check if any rule blocks plan generation
            if self.handbook_parser.should_block(matched_rules):
                logger.warning(f"Plan generation blocked by handbook rules for task {task.id}")
                raise ValueError("Plan generation blocked by handbook rules")

            # Build system prompt with handbook rules
            system_prompt = self._build_system_prompt(matched_rules)

            # Build user prompt
            user_prompt = self._build_user_prompt(task)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Parse response
            response_text = response.content[0].text
            plan_data = self._parse_response(response_text)

            # Create Plan object
            plan = Plan(
                task_id=task.id,
                steps=plan_data.get("steps", []),
                model_used=self.model,
                generation_time_ms=int((time.time() - start_time) * 1000),
            )

            # Apply handbook rules to plan
            plan.handbook_rules_applied = [rule.title for rule in matched_rules]
            plan.approval_checkpoints = self.handbook_parser.get_approval_checkpoints(
                matched_rules, plan.steps
            )
            plan.warnings = self.handbook_parser.get_warnings(matched_rules)

            logger.info(
                f"Generated plan {plan.id} with {len(plan.steps)} steps "
                f"in {plan.generation_time_ms}ms"
            )

            return plan

        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            raise
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            raise

    def _build_system_prompt(self, matched_rules: List) -> str:
        """
        Build system prompt with handbook rules

        Args:
            matched_rules: List of matched HandbookRule objects

        Returns:
            System prompt string
        """
        rules_text = ""
        if matched_rules:
            rules_text = "\n\nCompany Handbook Rules:\n"
            for rule in matched_rules:
                rules_text += f"- {rule.title}: {rule.rule_text}\n"

        return f"""You are an AI assistant helping to create action plans for tasks.
{rules_text}
Your task is to:
1. Analyze the task content carefully
2. Apply relevant handbook rules from the list above
3. Generate numbered action steps (be specific and actionable)
4. Identify steps that need human approval based on handbook rules
5. Include warnings for sensitive or risky actions

Return your response in this format:

STEPS:
1. [First step]
2. [Second step]
3. [Third step]

APPROVAL_NEEDED:
[List step numbers that need approval, e.g., "2, 4"]

WARNINGS:
[Any warnings or cautions]
"""

    def _build_user_prompt(self, task: Task) -> str:
        """
        Build user prompt with task details

        Args:
            task: Task object

        Returns:
            User prompt string
        """
        return f"""Task: {task.title}

Content:
{task.content}

Generate an action plan following the handbook rules. Be specific and actionable."""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude response into structured data

        Args:
            response_text: Response from Claude

        Returns:
            Dictionary with steps, approval_needed, warnings
        """
        lines = response_text.strip().split("\n")
        steps = []
        approval_needed = []
        warnings = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("STEPS:"):
                current_section = "steps"
                continue
            elif line.startswith("APPROVAL_NEEDED:"):
                current_section = "approval"
                continue
            elif line.startswith("WARNINGS:"):
                current_section = "warnings"
                continue

            if not line:
                continue

            if current_section == "steps":
                # Extract step text (remove number prefix)
                if line[0].isdigit():
                    step_text = line.split(".", 1)[1].strip() if "." in line else line
                    steps.append(step_text)

            elif current_section == "approval":
                # Parse approval step numbers
                if line and line[0].isdigit():
                    # Extract numbers from line
                    import re
                    numbers = re.findall(r"\d+", line)
                    approval_needed.extend([int(n) - 1 for n in numbers])  # Convert to 0-based

            elif current_section == "warnings":
                if line and not line.startswith("-"):
                    warnings.append(line)
                elif line.startswith("-"):
                    warnings.append(line[1:].strip())

        return {
            "steps": steps,
            "approval_needed": approval_needed,
            "warnings": warnings,
        }
