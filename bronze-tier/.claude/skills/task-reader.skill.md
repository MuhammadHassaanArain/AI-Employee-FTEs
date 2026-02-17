# task-reader

Read task files from the Needs_Action folder to understand what work needs to be done.

## Purpose

This skill allows Claude Code to read pending tasks from the Obsidian vault's Needs_Action folder. Tasks contain the original file content, metadata, and context needed for the AI Employee to generate actionable plans.

## When to Use

- When processing tasks from the Needs_Action queue
- When Claude Code needs to understand what work is pending
- At the start of each task processing cycle

## Inputs

- **task_id** (optional): Specific task UUID to read. If not provided, reads the oldest pending task.
- **vault_path** (optional): Path to Obsidian vault. Defaults to `./ai_employee_vault`

## Outputs

Returns task information including:
- Task ID (UUID)
- Title (extracted from content)
- Full content (original file text)
- Status (needs_action, processing, done, error)
- Source path (where file was detected)
- Original filename
- Timestamps (created_at, detected_at)
- File size

## Allowed File Operations

- **Read**: Task markdown files in `{vault_path}/Needs_Action/task-*.md`
- **Read**: Company handbook at `{vault_path}/Company_Handbook.md` (for context)

## Example Usage

```
Read the next pending task from Needs_Action folder.
```

## Implementation Notes

- Tasks are stored as markdown files with YAML frontmatter
- Task files follow naming pattern: `task-{uuid}.md`
- Oldest tasks (by creation time) should be processed first
- This skill is READ-ONLY and never modifies task files
