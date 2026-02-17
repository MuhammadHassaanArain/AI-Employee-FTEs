# plan-writer

Write AI-generated action plans into task files.

## Purpose

This skill allows Claude Code to append actionable plans to task files after reasoning about the task content and handbook rules. Plans include numbered steps, approval checkpoints for sensitive actions, and warnings.

## When to Use

- After reading and analyzing a task
- After applying handbook rules to determine required actions
- Before moving a task to Done folder

## Inputs

- **task_id** (required): UUID of the task to update
- **plan_steps** (required): List of actionable steps (strings)
- **approval_checkpoints** (optional): List of step indices requiring human approval
- **warnings** (optional): List of warning messages
- **handbook_rules_applied** (optional): List of handbook rules that influenced the plan

## Outputs

- Updated task file with appended plan section
- Confirmation message with task ID and number of steps

## Allowed File Operations

- **Read**: Task file at `{vault_path}/Needs_Action/task-{task_id}.md`
- **Append**: Plan section to the same task file

## Plan Format

Plans are appended to task files using this format:

```markdown
---

## AI Generated Plan

1. First action step
2. Second action step
3. **[APPROVAL REQUIRED]** Sensitive action requiring approval
4. Final action step

### Warnings
- Warning message if applicable

### Handbook Rules Applied
- [CRITICAL] Never delete original files
- [HIGH] Ask for approval before sending emails
```

## Example Usage

```
Write a plan for task 07f4fefc-b90b-497b-a85a-657d7a809f4f with steps:
1. Review email content
2. Draft response
3. Request approval before sending
```

## Implementation Notes

- Plans are appended to existing task content, never replacing it
- Approval checkpoints are marked with **[APPROVAL REQUIRED]** prefix
- This skill does NOT move tasks between folders
- Plans should be specific and actionable, not generic templates
