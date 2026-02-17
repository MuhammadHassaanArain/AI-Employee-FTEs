# task-mover

Move tasks between folders (Needs_Action → Done).

## Purpose

This skill allows Claude Code to move completed tasks from the Needs_Action folder to the Done folder after successfully generating and writing a plan.

## When to Use

- After successfully writing a plan to a task file
- When a task has been fully processed and is ready for archival
- Never before a plan has been generated

## Inputs

- **task_id** (required): UUID of the task to move
- **source_folder** (optional): Source folder name. Defaults to "Needs_Action"
- **target_folder** (optional): Target folder name. Defaults to "Done"

## Outputs

- Task file moved from source to target folder
- Task status updated to "done" in YAML frontmatter
- Confirmation message with old and new paths

## Allowed File Operations

- **Read**: Task file at `{vault_path}/{source_folder}/task-{task_id}.md`
- **Write**: Task file to `{vault_path}/{target_folder}/task-{task_id}.md`
- **Delete**: Original file from source folder after successful copy

## Example Usage

```
Move task 07f4fefc-b90b-497b-a85a-657d7a809f4f to Done folder.
```

## Implementation Notes

- Task status in YAML frontmatter is updated to "done"
- Original file is deleted only after successful write to target
- If target file already exists, operation fails with error
- This is a destructive operation - use only after plan is written
- Preserves all task content including the generated plan
