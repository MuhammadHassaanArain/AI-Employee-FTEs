# dashboard-updater

Update the Obsidian dashboard with task counts and activity logs.

## Purpose

This skill allows Claude Code to update the Dashboard.md file with current task counts and recent activity. This provides visibility into the AI Employee's work and system status.

## When to Use

- After processing a task (moving from Needs_Action to Done)
- When task counts change
- When logging significant actions or errors

## Inputs

- **action_type** (required): Type of action (task_processed, error, system_start, etc.)
- **details** (required): Description of what happened
- **task_id** (optional): UUID of related task
- **outcome** (optional): Result of action (success, failure, skipped)

## Outputs

- Updated Dashboard.md with current task counts
- New activity log entry appended
- Confirmation message

## Allowed File Operations

- **Read**: Dashboard at `{vault_path}/Dashboard.md`
- **Write**: Updated dashboard content
- **Read**: Folder contents to count tasks (Inbox, Needs_Action, Done)

## Dashboard Format

```markdown
# AI Employee Dashboard

## Task Counts
- Inbox: 6
- Needs_Action: 0
- Done: 5

## Activity Log

[2026-02-17T07:19:32.932778Z] TASK_MOVED 7f0b2f0c... Moved task to Done success
[2026-02-17T07:19:32.932513Z] PLAN_GENERATED 7f0b2f0c... Generated plan with 7 steps success
```

## Example Usage

```
Update dashboard after processing task 07f4fefc-b90b-497b-a85a-657d7a809f4f.
Log: "Generated plan with 5 steps" - outcome: success
```

## Implementation Notes

- Task counts are calculated by scanning folder contents
- Activity log shows most recent entries first
- Timestamps use ISO 8601 format with UTC timezone
- Dashboard is human-readable in Obsidian
- Keep activity log concise (last 20 entries)
