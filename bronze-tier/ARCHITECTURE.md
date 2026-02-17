# AI Employee - Bronze Tier (Claude Code Integration)

## Architecture Overview

This is a TRUE "Personal AI Employee" where **Claude Code is the brain** and Python provides the senses.

### Components

1. **Python Watchers** (Senses)
   - Monitor Inbox folder for new files
   - Create task files in Needs_Action
   - Tasks are created WITHOUT plans

2. **Claude Code** (Brain)
   - Reads tasks from Needs_Action
   - Reasons about each task contextually
   - Generates specific, actionable plans
   - Applies handbook rules
   - Moves completed tasks to Done

3. **Agent Skills** (Tools)
   - task-reader: Read pending tasks
   - handbook-reader: Read behavioral rules
   - plan-writer: Write AI-generated plans
   - task-mover: Move tasks between folders
   - dashboard-updater: Update status dashboard

## Execution Flow

```
1. User drops file in Inbox/
   ↓
2. Python watcher detects file
   ↓
3. Task created in Needs_Action/ (NO PLAN)
   ↓
4. User runs: python claude_runner.py
   ↓
5. Claude Code invoked with task context
   ↓
6. Claude Code uses task-reader skill
   ↓
7. Claude Code uses handbook-reader skill
   ↓
8. Claude Code REASONS about task (AI, not templates)
   ↓
9. Claude Code generates contextual plan
   ↓
10. Claude Code uses plan-writer skill
   ↓
11. Claude Code uses task-mover skill
   ↓
12. Claude Code uses dashboard-updater skill
   ↓
13. Task moved to Done/ with AI-generated plan
```

## Key Differences from Previous Implementation

### BEFORE (Fake AI)
- Python generated plans using hardcoded templates
- Keyword matching determined task type
- All email tasks got identical plans
- No actual AI reasoning

### AFTER (Real AI)
- Claude Code generates plans dynamically
- Each task gets a unique, contextual plan
- Real AI reasoning based on task content
- Handbook rules applied intelligently

## Usage

### 1. Initialize Vault
```bash
python -m ai_employee init
```

### 2. Start File Watcher
```bash
python -m ai_employee watch
```

### 3. Drop Files in Inbox
```bash
echo "Schedule meeting with engineering team" > ai_employee_vault/Inbox/meeting.txt
```

### 4. Process Tasks with Claude Code
```bash
python claude_runner.py
```

Claude Code will:
- Read the task
- Read the handbook
- Reason about what needs to be done
- Generate a specific plan
- Write the plan to the task file
- Move task to Done
- Update dashboard

## Agent Skills

All skills are defined in `.claude/skills/`:

- **task-reader.skill.md** - Read tasks from Needs_Action
- **handbook-reader.skill.md** - Read Company_Handbook.md
- **plan-writer.skill.md** - Write plans to task files
- **task-mover.skill.md** - Move tasks to Done
- **dashboard-updater.skill.md** - Update Dashboard.md

## No External APIs Required

This implementation does NOT use:
- Anthropic API
- Any external AI services
- API keys or credentials

Claude Code runs locally and processes tasks using its native capabilities.

## Bronze Tier Constraints

- Single input source (Inbox folder only)
- File-based storage (no database)
- Local processing only
- Manual task execution (plans are generated, not executed)
- No Gmail integration (Silver/Gold tier)
- No web interface (Obsidian only)

## Validation

To verify the system works correctly:

1. Drop a test file in Inbox
2. Verify task created in Needs_Action WITHOUT a plan
3. Run claude_runner.py
4. Verify Claude Code generates a UNIQUE plan
5. Verify task moved to Done with plan
6. Drop another file with different content
7. Verify it gets a DIFFERENT plan (not a template)

## Success Criteria

✓ Tasks created without pre-generated plans
✓ Claude Code processes tasks dynamically
✓ Each task gets a contextual, unique plan
✓ No keyword-based templates exist
✓ Handbook rules applied intelligently
✓ Tasks only move to Done after Claude Code processing
