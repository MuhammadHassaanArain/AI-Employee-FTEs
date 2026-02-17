# Personal AI Employee - Bronze Tier (Claude Code Integration)

A TRUE AI Employee where **Claude Code is the reasoning engine** and Python provides the sensory input.

## What Makes This Different

### Previous Implementation (Fake AI)
- Python generated plans using hardcoded templates
- Keyword matching: "email" → generic email steps
- All similar tasks got identical plans
- No actual AI reasoning

### Current Implementation (Real AI)
- **Claude Code generates plans dynamically**
- Each task gets unique, contextual reasoning
- Real AI decision-making based on content
- Handbook rules applied intelligently

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                           ↓                                  │
│                  Drops file in Inbox/                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   PYTHON WATCHER (Senses)                    │
│  - Detects new files                                         │
│  - Creates task in Needs_Action/                             │
│  - Task has NO PLAN (just content + metadata)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  CLAUDE CODE (Brain)                         │
│  1. Reads task using task-reader skill                       │
│  2. Reads handbook using handbook-reader skill               │
│  3. REASONS about task (AI, not templates)                   │
│  4. Generates contextual plan                                │
│  5. Writes plan using plan-writer skill                      │
│  6. Moves task using task-mover skill                        │
│  7. Updates dashboard using dashboard-updater skill          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                            │
│  - Done/ folder contains completed tasks with AI plans       │
│  - Dashboard.md shows status                                 │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Initialize Vault
```bash
python -m ai_employee init
```

### 3. Start File Watcher (Terminal 1)
```bash
python -m ai_employee watch
```

### 4. Drop a Test File (Terminal 2)
```bash
echo "Schedule engineering team meeting for next Monday to discuss API architecture" > ai_employee_vault/Inbox/meeting.txt
```

### 5. Process with Claude Code (Terminal 2)
```bash
python claude_runner.py
```

Claude Code will now:
- Read the task
- Understand the context
- Generate a specific plan
- Write it to the task file
- Move task to Done

### 6. Verify Results
```bash
# Check the task in Done folder
cat ai_employee_vault/Done/task-*.md

# Check dashboard
cat ai_employee_vault/Dashboard.md
```

## Agent Skills

Claude Code uses these skills to process tasks:

| Skill | Purpose | File Operations |
|-------|---------|-----------------|
| **task-reader** | Read pending tasks | Read Needs_Action/*.md |
| **handbook-reader** | Read behavioral rules | Read Company_Handbook.md |
| **plan-writer** | Write AI-generated plans | Append to task files |
| **task-mover** | Move completed tasks | Move Needs_Action → Done |
| **dashboard-updater** | Update status dashboard | Edit Dashboard.md |

All skills are defined in `.claude/skills/`

## Project Structure

```
bronze-tier/
├── ai_employee/              # Python package (senses only)
│   ├── watcher/             # File monitoring
│   ├── processor/           # Task detection (no plan generation)
│   ├── vault/               # Vault management
│   ├── models/              # Data structures
│   └── utils/               # Logging, file tracking
├── .claude/
│   └── skills/              # Agent Skills for Claude Code
│       ├── task-reader.skill.md
│       ├── handbook-reader.skill.md
│       ├── plan-writer.skill.md
│       ├── task-mover.skill.md
│       └── dashboard-updater.skill.md
├── ai_employee_vault/       # Obsidian vault (created by init)
│   ├── Inbox/              # Drop files here
│   ├── Needs_Action/       # Tasks waiting for Claude Code
│   ├── Done/               # Completed tasks with AI plans
│   ├── Dashboard.md        # Status overview
│   └── Company_Handbook.md # Behavioral rules
├── claude_runner.py         # Invokes Claude Code to process tasks
└── ARCHITECTURE.md          # Detailed architecture docs
```

## How It Works

### Task Creation (Python)
1. Watcher detects new file in Inbox
2. Creates task file in Needs_Action with:
   - YAML frontmatter (id, status, timestamps)
   - Original file content
   - **NO PLAN** (this is crucial)

### Task Processing (Claude Code)
1. `claude_runner.py` identifies pending tasks
2. Invokes Claude Code with task context
3. Claude Code uses skills to:
   - Read task content
   - Read handbook rules
   - **Reason about the task** (AI, not templates)
   - Generate specific, actionable plan
   - Write plan to task file
   - Move task to Done
   - Update dashboard

### Key Insight
The plan is generated by **Claude Code's reasoning**, not by Python templates. Different tasks get different plans based on their actual content.

## Example: Different Tasks, Different Plans

### Task 1: "Schedule meeting with engineering team"
Claude Code generates:
1. Identify required attendees
2. Check calendar availability
3. Prepare meeting agenda
4. Send calendar invites
5. Log meeting scheduled

### Task 2: "Send invoice to client ABC"
Claude Code generates:
1. Locate invoice template
2. Fill in client details and amounts
3. **[APPROVAL REQUIRED]** Review invoice before sending
4. Send invoice via email
5. Log invoice sent

Notice: Different tasks → Different plans → Different approval checkpoints

## Handbook Rules

Edit `ai_employee_vault/Company_Handbook.md` to customize behavior:

```markdown
# Company Handbook

## Rules
- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.
- [MEDIUM] Summaries under 200 words.
- [LOW] Use bullet points when possible.
```

Claude Code applies these rules when generating plans.

## Commands

### Initialize Vault
```bash
python -m ai_employee init [--vault-path PATH]
```

### Start File Watcher
```bash
python -m ai_employee watch [--vault-path PATH] [--watch-folder PATH]
```

### Process Tasks with Claude Code
```bash
python claude_runner.py
```

### Show Configuration
```bash
python -m ai_employee config --show
```

## No External APIs Required

This implementation does NOT use:
- ❌ Anthropic API
- ❌ OpenAI API
- ❌ Any external AI services
- ❌ API keys or credentials

Claude Code runs locally using its native capabilities.

## Bronze Tier Constraints

By design, Bronze Tier has these limitations:
- Single input source (Inbox folder only)
- File-based storage (no database)
- Local processing only
- Manual plan execution (plans are generated, not executed)
- No Gmail integration (Silver/Gold tier)
- No web interface (Obsidian only)

## Validation

To verify the system works correctly:

1. **Drop test file**: `echo "Test task" > ai_employee_vault/Inbox/test.txt`
2. **Verify task created**: Check `ai_employee_vault/Needs_Action/` - task should have NO plan
3. **Run Claude Code**: `python claude_runner.py`
4. **Verify unique plan**: Check `ai_employee_vault/Done/` - task should have AI-generated plan
5. **Drop different file**: `echo "Different task" > ai_employee_vault/Inbox/test2.txt`
6. **Verify different plan**: New task should get a DIFFERENT plan (not a template)

## Troubleshooting

### "No tasks to process"
- Check if files are in `ai_employee_vault/Inbox/`
- Verify watcher is running: `python -m ai_employee watch`
- Check `ai_employee_vault/Needs_Action/` for pending tasks

### Tasks not being detected
- Ensure watcher is running in a separate terminal
- Check file permissions on Inbox folder
- View logs: `tail -f ai_employee_vault/activity.log`

### Plans look generic
- This means Claude Code is not being invoked correctly
- Verify `claude_runner.py` is being used (not old Python automation)
- Check that `local_plan_generator.py` has been deleted

## Development

### File Changes from Previous Version

**Deleted:**
- `ai_employee/processor/local_plan_generator.py` (fake AI)

**Modified:**
- `ai_employee/processor/task_processor.py` (simplified to detection only)
- `ai_employee/__main__.py` (removed autonomous processing loop)
- `requirements.txt` (removed anthropic dependency)

**Created:**
- `.claude/skills/task-reader.skill.md`
- `.claude/skills/handbook-reader.skill.md`
- `.claude/skills/plan-writer.skill.md`
- `.claude/skills/task-mover.skill.md`
- `.claude/skills/dashboard-updater.skill.md`
- `claude_runner.py` (Claude Code orchestrator)
- `ARCHITECTURE.md` (detailed architecture docs)

## License

MIT License - See LICENSE file for details.

## Version

2.0.0 - Bronze Tier (Claude Code Integration)

---

**Status**: Transformed ✓

This is now a TRUE AI Employee where Claude Code does the reasoning.
