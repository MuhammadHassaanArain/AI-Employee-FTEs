#!/usr/bin/env python3
"""
Claude Code Runner (Bronze Tier)

This script invokes Claude Code to process tasks from /Needs_Action.
Claude Code reads tasks, reasons about them, generates plans, and moves them to Done.

This is NOT an API client - it's a process orchestrator that lets Claude Code
do the actual reasoning and decision-making.
"""

import sys
import subprocess
from pathlib import Path
from ai_employee.processor.task_processor import TaskProcessor
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


def process_next_task(vault_path: Path) -> bool:
    """
    Process the next pending task using Claude Code.

    This function identifies the next task and invokes Claude Code to process it.
    Claude Code will:
    1. Read the task using task-reader skill
    2. Read handbook using handbook-reader skill
    3. Reason about the task (AI, not templates)
    4. Generate a contextual plan
    5. Write the plan using plan-writer skill
    6. Move task to Done using task-mover skill
    7. Update dashboard using dashboard-updater skill

    Args:
        vault_path: Path to Obsidian vault

    Returns:
        True if a task was processed, False if no tasks pending
    """
    processor = TaskProcessor(vault_path)
    pending_tasks = processor.get_pending_tasks()

    if not pending_tasks:
        logger.info("No pending tasks in Needs_Action")
        return False

    # Get the oldest task
    task_file = pending_tasks[0]
    task_id = task_file.stem.replace("task-", "")

    logger.info(f"Processing task: {task_id}")
    logger.info(f"Task file: {task_file}")

    # Invoke Claude Code to process this task
    # Claude Code will use the defined skills to:
    # - Read the task
    # - Read the handbook
    # - Generate a plan
    # - Write the plan
    # - Move the task
    # - Update the dashboard

    prompt = f"""You are the AI Employee (Bronze Tier).

A new task is waiting in the Needs_Action folder.

TASK FILE: {task_file}

YOUR WORKFLOW:
1. Use the task-reader skill to read the task content
2. Use the handbook-reader skill to read Company_Handbook.md
3. Analyze the task and determine what actions are needed
4. Generate a contextual, specific plan (NOT a generic template)
5. Apply handbook rules (add approval checkpoints for sensitive actions)
6. Use the plan-writer skill to write the plan into the task file
7. Use the task-mover skill to move the task to Done
8. Use the dashboard-updater skill to log the completion

IMPORTANT:
- Generate plans based on actual task content, not templates
- Different tasks should get different plans
- Apply handbook rules strictly
- Add approval checkpoints for sensitive actions (emails, payments, etc.)
- Be specific and actionable

Process this task now."""

    print("\n" + "="*80)
    print("INVOKING CLAUDE CODE TO PROCESS TASK")
    print("="*80)
    print(f"\nTask ID: {task_id}")
    print(f"Task File: {task_file}")
    print("\nClaude Code will now:")
    print("  1. Read the task")
    print("  2. Read the handbook")
    print("  3. Reason about the task")
    print("  4. Generate a contextual plan")
    print("  5. Write the plan")
    print("  6. Move task to Done")
    print("  7. Update dashboard")
    print("\n" + "="*80 + "\n")

    # For now, print the prompt that would be sent to Claude Code
    # In a real implementation, this would invoke Claude Code via CLI
    print("PROMPT FOR CLAUDE CODE:")
    print(prompt)
    print("\n" + "="*80 + "\n")

    return True


def main():
    """Main entry point for Claude Code runner"""
    vault_path = Path("./ai_employee_vault")

    if not vault_path.exists():
        print(f"ERROR: Vault not found at {vault_path}")
        print("Run: python -m ai_employee init")
        sys.exit(1)

    print("Claude Code Runner (Bronze Tier)")
    print(f"Vault: {vault_path}")
    print("-" * 80)

    # Process one task
    processed = process_next_task(vault_path)

    if processed:
        print("\nTask processing initiated.")
        print("Claude Code should now process the task using the defined skills.")
    else:
        print("\nNo tasks to process.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
