# Data Model: Personal AI Employee Bronze Tier

**Feature**: 001-ai-employee-bronze
**Date**: 2026-02-15
**Purpose**: Define data structures and relationships for task management system

## Overview

The Bronze tier AI Employee uses a file-based data model where all entities are stored as markdown files with YAML frontmatter. This approach ensures Obsidian compatibility and human readability while maintaining structured metadata.

## Core Entities

### 1. Task

**Purpose**: Represents a work item captured from the monitored folder

**Storage Location**: `/Needs_Action/` (active) or `/Done/` (completed)

**File Naming**: `task-{uuid}.md`

**Schema**:

```yaml
id: string (UUID v4)
  # Unique identifier for the task
  # Example: "550e8400-e29b-41d4-a716-446655440000"

title: string (max 200 chars)
  # Human-readable task title
  # Derived from filename or first line of content
  # Example: "Review Q4 Budget Report"

source_path: string (absolute path)
  # Original file location in monitored folder
  # Example: "/home/user/monitored/budget_report.pdf"

created_at: datetime (ISO 8601)
  # When the task entity was created
  # Example: "2026-02-15T10:30:00Z"

status: enum
  # Current task state
  # Values: "needs_action" | "processing" | "done" | "error"
  # Default: "needs_action"

original_filename: string
  # Original file name from monitored folder
  # Example: "budget_report.pdf"

file_size: integer (bytes)
  # Size of original file
  # Example: 2048576

detected_at: datetime (ISO 8601)
  # When file was first detected by watcher
  # Example: "2026-02-15T10:30:15Z"

error_message: string (optional)
  # Error details if status is "error"
  # Example: "Failed to parse file content"
```

**Content Structure**:
```markdown
---
[YAML frontmatter with schema above]
---

# {title}

{Original file content or extracted text}

## Metadata
- Source: {source_path}
- Detected: {detected_at}
- Size: {file_size} bytes
```

**State Transitions**:
```
needs_action → processing (when Claude starts generating plan)
processing → done (when plan created and file moved to /Done)
processing → error (when plan generation fails after retries)
error → needs_action (manual retry by user)
```

**Validation Rules**:
- `id` must be valid UUID v4
- `title` cannot be empty
- `source_path` must be absolute path
- `status` must be one of allowed enum values
- `file_size` must be positive integer
- `created_at` and `detected_at` must be valid ISO 8601 timestamps

---

### 2. Plan

**Purpose**: AI-generated action plan for a task

**Storage Location**: `/Plans/`

**File Naming**: `plan-{task_uuid}.md`

**Schema**:

```yaml
id: string (UUID v4)
  # Unique identifier for the plan
  # Example: "660e8400-e29b-41d4-a716-446655440001"

task_id: string (UUID v4)
  # Reference to associated task
  # Example: "550e8400-e29b-41d4-a716-446655440000"

created_at: datetime (ISO 8601)
  # When plan was generated
  # Example: "2026-02-15T10:31:00Z"

handbook_rules_applied: list[string]
  # Rules from Company_Handbook.md that influenced this plan
  # Example: ["Human approval required for payments >$50"]

approval_checkpoints: list[integer]
  # Step indices (0-based) requiring human approval
  # Example: [2, 5] means steps 3 and 6 need approval

warnings: list[string] (optional)
  # Cautions or alerts about the task
  # Example: ["Task involves financial data"]

model_used: string
  # Claude model version used for generation
  # Example: "claude-3-5-sonnet-20241022"

generation_time_ms: integer
  # Time taken to generate plan
  # Example: 3500
```

**Content Structure**:
```markdown
---
[YAML frontmatter with schema above]
---

# Action Plan: {task_title}

**Task Reference**: [[task-{task_id}]]

## Steps

1. {First action step}
2. {Second action step}
3. **[APPROVAL REQUIRED]** {Step requiring approval}
4. {Continue with remaining steps}

## Handbook Rules Applied

- {Rule 1 text}
- {Rule 2 text}

## Warnings

- {Warning 1}
- {Warning 2}

## Next Actions

{Summary of what user should do next}
```

**Relationships**:
- One-to-one with Task (each task has at most one plan)
- References task via `task_id` field
- Obsidian link: `[[task-{task_id}]]` for navigation

**Validation Rules**:
- `id` and `task_id` must be valid UUID v4
- `task_id` must reference an existing task
- `approval_checkpoints` indices must be valid (within step count)
- `handbook_rules_applied` must match rules in Company_Handbook.md
- `generation_time_ms` must be positive integer

---

### 3. Handbook Rule

**Purpose**: Behavioral constraint or guideline for plan generation

**Storage Location**: `/Company_Handbook.md` (single file)

**Schema** (per rule):

```yaml
# Rules are stored as markdown sections in Company_Handbook.md
# Each rule has implicit structure:

rule_text: string
  # The actual rule statement
  # Example: "Human approval required for payments >$50"

priority: enum
  # Importance level
  # Values: "critical" | "high" | "medium" | "low"
  # Inferred from section heading level

keywords: list[string]
  # Terms that trigger this rule
  # Example: ["payment", "transfer", "invoice", "$"]

action: enum
  # What to do when rule matches
  # Values: "flag" | "require_approval" | "warn" | "block"
  # Inferred from rule text
```

**File Structure** (Company_Handbook.md):
```markdown
# Company Handbook

## Critical Rules

### Human approval required for payments >$50
**Keywords**: payment, transfer, invoice, $, money
**Action**: require_approval

Any task involving financial transactions over $50 must include an explicit approval checkpoint before execution.

### Never share sensitive data externally
**Keywords**: password, API key, token, credential, secret
**Action**: block

Tasks must not include steps that transmit sensitive information outside the local system.

## High Priority Rules

### Always flag urgent emails
**Keywords**: urgent, ASAP, immediate, critical
**Action**: flag

Tasks containing urgent keywords should be highlighted in the plan for immediate attention.

## Medium Priority Rules

### Log all external communications
**Keywords**: email, send, message, notify
**Action**: warn

Plans involving external communications should include logging steps.
```

**Parsing Logic**:
- Section headings (###) define individual rules
- Keywords extracted from **Keywords** line
- Action extracted from **Action** line
- Priority determined by parent section (## heading)

**Validation Rules**:
- Each rule must have a heading
- Keywords must be comma-separated
- Action must be one of allowed enum values
- Rule text cannot be empty

---

### 4. Activity Log Entry

**Purpose**: Record of system actions for audit and debugging

**Storage Location**: `/activity.log` (append-only text file)

**Schema** (per line):

```
[timestamp] [level] [action_type] [task_id] [details] [outcome]

timestamp: datetime (ISO 8601)
  # When action occurred
  # Example: "2026-02-15T10:30:00Z"

level: enum
  # Log severity
  # Values: "DEBUG" | "INFO" | "WARNING" | "ERROR"

action_type: enum
  # Type of action
  # Values: "file_detected" | "task_created" | "plan_generated" |
  #         "task_moved" | "error" | "warning" | "system_start" | "system_stop"

task_id: string (UUID v4 or "N/A")
  # Associated task if applicable
  # Example: "550e8400-e29b-41d4-a716-446655440000"

details: string
  # Human-readable description
  # Example: "Detected new file: budget_report.pdf"

outcome: enum
  # Result of action
  # Values: "success" | "failure" | "skipped" | "pending"
```

**Log Format**:
```
[2026-02-15T10:30:00Z] INFO file_detected N/A Detected new file: budget_report.pdf success
[2026-02-15T10:30:15Z] INFO task_created 550e8400-e29b-41d4-a716-446655440000 Created task: Review Q4 Budget Report success
[2026-02-15T10:31:00Z] INFO plan_generated 550e8400-e29b-41d4-a716-446655440000 Generated plan with 5 steps success
[2026-02-15T10:31:05Z] INFO task_moved 550e8400-e29b-41d4-a716-446655440000 Moved task to /Done success
[2026-02-15T10:31:10Z] ERROR plan_generated 660e8400-e29b-41d4-a716-446655440002 Claude API rate limit exceeded failure
```

**Dashboard Representation**:
- Last 10 entries displayed in Dashboard.md
- Formatted as markdown list with timestamps
- Color coding via Obsidian callouts (info/warning/error)

**Validation Rules**:
- Timestamp must be valid ISO 8601
- Level must be one of allowed enum values
- Action type must be one of allowed enum values
- Task ID must be valid UUID or "N/A"
- Outcome must be one of allowed enum values

---

### 5. Dashboard

**Purpose**: Real-time system status and activity summary

**Storage Location**: `/Dashboard.md` (root of vault)

**Schema** (markdown structure):

```markdown
# AI Employee Dashboard

**Last Updated**: {timestamp}
**System Status**: {status}

## Task Counts

- **Needs Action**: {count} tasks
- **In Progress**: {count} tasks
- **Completed Today**: {count} tasks
- **Total Completed**: {count} tasks
- **Errors**: {count} tasks

## Recent Activity (Last 10 Actions)

1. [{timestamp}] {action_type}: {details} - {outcome}
2. [{timestamp}] {action_type}: {details} - {outcome}
...

## System Configuration

- **Monitored Folder**: {path}
- **Vault Path**: {path}
- **Max Iterations**: {number}
- **Claude Model**: {model_name}

## Quick Links

- [[Company_Handbook]]
- [[Needs_Action/]]
- [[Plans/]]
- [[Done/]]
```

**Update Triggers**:
- After each file detection
- After each plan generation
- After each task completion
- On system startup/shutdown
- On error occurrence

**Validation Rules**:
- Counts must be non-negative integers
- Timestamp must be current (within last 5 minutes)
- Status must be "Running" | "Idle" | "Error"
- Paths must be valid and accessible

---

## Entity Relationships

```
Task (1) ←→ (0..1) Plan
  - One task can have zero or one plan
  - Plan references task via task_id

Task (1) ←→ (N) Activity Log Entry
  - One task generates multiple log entries
  - Log entries reference task via task_id

Handbook Rule (N) ←→ (N) Plan
  - Multiple rules can apply to one plan
  - One rule can apply to multiple plans
  - Relationship tracked via handbook_rules_applied field

Dashboard (1) ←→ (N) Task
  - Dashboard aggregates counts from all tasks
  - No direct reference, computed on update
```

## Data Flow

```
1. File detected in monitored folder
   ↓
2. Task entity created in /Needs_Action
   ↓
3. Activity log entry: file_detected
   ↓
4. Dashboard updated: increment Needs Action count
   ↓
5. Claude API called with task + handbook rules
   ↓
6. Plan entity created in /Plans
   ↓
7. Activity log entry: plan_generated
   ↓
8. Task moved to /Done, status updated
   ↓
9. Activity log entry: task_moved
   ↓
10. Dashboard updated: decrement Needs Action, increment Completed
```

## Storage Estimates

**Bronze Tier Scale** (100 tasks/day):

| Entity | Size per Item | Daily Volume | Monthly Storage |
|--------|--------------|--------------|-----------------|
| Task | ~5 KB | 100 | ~15 MB |
| Plan | ~3 KB | 100 | ~9 MB |
| Log Entry | ~200 bytes | 500 | ~3 MB |
| Dashboard | ~2 KB | 1 (updated) | ~2 KB |
| Handbook | ~5 KB | 1 (static) | ~5 KB |

**Total Monthly**: ~27 MB (well within 1GB vault limit)

## Backup & Recovery

**Backup Strategy**:
- User responsible for vault backup (Obsidian sync or manual)
- No automated backup in Bronze tier
- Activity log provides audit trail for recovery

**Recovery Scenarios**:
1. **Lost task file**: Recreate from activity log + original file
2. **Lost plan file**: Regenerate via Claude API
3. **Corrupted dashboard**: Rebuild from task counts
4. **Lost handbook**: Restore from git or user backup

## Future Considerations (Silver/Gold Tiers)

- Add `priority` field to Task for intelligent scheduling
- Add `tags` field for categorization
- Add `dependencies` field for task relationships
- Add `estimated_time` field for workload planning
- Migrate to SQLite for better querying
- Add full-text search across tasks and plans
