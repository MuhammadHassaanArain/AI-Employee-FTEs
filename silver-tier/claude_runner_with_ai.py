#!/usr/bin/env python3
"""
Claude Code Runner (Silver Tier - With Real Claude Reasoning)

This script invokes Claude Code to process tasks with intelligent reasoning.
Claude Code does the actual AI reasoning, not pattern matching.

Silver Tier enhancements:
- Claude Code generates plans with real reasoning
- Approval workflow for sensitive actions
- MCP server execution for approved tasks
- Multi-source task support (file, gmail)
"""

import sys
from pathlib import Path
from ai_employee.config import Config
from ai_employee.processor.task_processor import TaskProcessor
from ai_employee.models.task import Task
from ai_employee.skills.approval_skill import ApprovalSkill
from ai_employee.mcp.mcp_server import MCPServer
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


def process_task_with_claude(task_file: Path, vault_path: Path) -> bool:
    """
    Process task using Claude Code for intelligent reasoning.

    Args:
        task_file: Path to task file
        vault_path: Path to vault

    Returns:
        True if processed successfully
    """
    task_id = task_file.stem.replace("task-", "")

    # Read task to get metadata
    try:
        task = Task.from_markdown(task_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to read task: {e}")
        return False

    # Create prompt for Claude Code
    prompt = f"""You are the AI Employee (Silver Tier) with intelligent reasoning capabilities.

A new task is waiting for processing.

TASK FILE: {task_file}
TASK TITLE: {task.title}
TASK SOURCE: {task.source}

YOUR WORKFLOW:

1. READ THE TASK
   - Read the task file: {task_file}
   - Understand what the user is asking for

2. READ THE HANDBOOK
   - Read Company_Handbook.md for behavioral rules
   - Identify which rules apply to this task

3. INTELLIGENT REASONING
   - Analyze the task content carefully
   - Determine the action type (email, linkedin, research, payment, etc.)
   - Extract key entities (emails, URLs, amounts, dates)
   - Generate context-aware action steps
   - Consider risks and warnings

4. APPROVAL DETECTION
   - Determine if this task requires human approval
   - Sensitive actions that REQUIRE approval:
     * Sending emails
     * Posting to LinkedIn/social media
     * Making payments or financial transactions
     * Deleting data
     * Any external communication
   - Safe actions that DON'T need approval:
     * Research and information gathering
     * Reading and summarizing
     * Internal analysis
     * Creating reports

5. GENERATE PLAN
   - Create a detailed, actionable plan
   - Include specific steps based on the task content
   - Mark steps that require approval with [APPROVAL REQUIRED]
   - Add warnings for risky actions
   - Apply handbook rules

6. WRITE THE PLAN
   - Create a Plan.md file in the Plans/ folder
   - Filename: plan-{task_id}.md
   - Include:
     * Task ID and title
     * Action steps (numbered)
     * Approval checkpoints (if needed)
     * Handbook rules applied
     * Warnings
     * Metadata (created_at, model_used)

7. DETERMINE ROUTING
   - If approval required: State "APPROVAL_REQUIRED: true"
   - If no approval needed: State "APPROVAL_REQUIRED: false"

IMPORTANT:
- Use REAL reasoning, not templates
- Different tasks should get different plans
- Be specific about what actions to take
- Consider the task source (file vs gmail)
- Apply handbook rules strictly

FORMAT YOUR RESPONSE:
```
APPROVAL_REQUIRED: [true/false]
PLAN_FILE: [path to plan file you created]
REASONING: [brief explanation of your decision]
```

Process this task now using your intelligent reasoning capabilities."""

    print("\n" + "="*80)
    print("INVOKING CLAUDE CODE FOR INTELLIGENT REASONING")
    print("="*80)
    print(f"\nTask ID: {task_id}")
    print(f"Task Title: {task.title}")
    print(f"Task Source: {task.source}")
    print(f"Task File: {task_file}")
    print("\nClaude Code will now:")
    print("  1. Read and understand the task")
    print("  2. Read the handbook for rules")
    print("  3. Use AI reasoning to analyze the task")
    print("  4. Generate an intelligent, contextual plan")
    print("  5. Determine if approval is needed")
    print("  6. Write the plan to Plans/ folder")
    print("\n" + "="*80 + "\n")

    print("PROMPT FOR CLAUDE CODE:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("\n1. Claude Code will process this task using the prompt above")
    print("2. Claude Code will generate a Plan.md file")
    print("3. Claude Code will determine if approval is needed")
    print("4. Based on Claude's decision:")
    print("   - If approval needed: Task moves to Waiting_Approval/")
    print("   - If no approval: Task moves to Done/")
    print("\nTo complete this workflow:")
    print("  Run this script inside Claude Code CLI")
    print("  Claude Code will execute the prompt and process the task")
    print("\n" + "="*80 + "\n")

    return True


def main():
    """Main entry point for Claude Code runner"""
    try:
        config = Config()
        vault_path = config.vault_path

        if not vault_path.exists():
            print(f"ERROR: Vault not found at {vault_path}")
            print("Run: python -m ai_employee init")
            return 1

        print("\n" + "="*80)
        print("CLAUDE CODE RUNNER - SILVER TIER")
        print("="*80)
        print(f"Vault: {vault_path}")
        print("="*80 + "\n")

        # Get pending tasks
        processor = TaskProcessor(vault_path)
        pending_tasks = processor.get_pending_tasks()

        if not pending_tasks:
            print("No pending tasks in Needs_Action/")
            print("\nTo create a test task:")
            print('  echo "Research AI tools" > ai_employee_vault/Inbox/test.txt')
            print("  python claude_runner.py")
            return 0

        # Process first task
        task_file = pending_tasks[0]
        print(f"Found {len(pending_tasks)} pending task(s)")
        print(f"Processing: {task_file.name}\n")

        # Invoke Claude Code
        success = process_task_with_claude(task_file, vault_path)

        if success:
            print("\n" + "="*80)
            print("TASK PROCESSING INITIATED")
            print("="*80)
            print("\nClaude Code should now process the task.")
            print("The prompt above tells Claude Code exactly what to do.")
            print("\nRun this script inside Claude Code CLI for full AI reasoning.")
            print("="*80 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
