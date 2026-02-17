# AI Employee (Bronze Tier) - Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
cd bronze-tier
pip install -e .
```

This installs the AI Employee package and all required dependencies.

### 2. Initialize the Vault

```bash
python -m ai_employee init
```

**Expected Output:**
```
[OK] Vault initialized at: ./ai_employee_vault
[OK] Open in Obsidian: ./ai_employee_vault

Next steps:
  1. Run: python -m ai_employee watch
  2. Drop files in: ./ai_employee_vault/Inbox
  3. Process tasks: python claude_runner.py
```

This creates the vault structure:
```
ai_employee_vault/
├── Inbox/              # Drop files here
├── Needs_Action/       # Tasks waiting to be processed
├── Done/               # Completed tasks with answers
├── Plans/              # Planning artifacts
├── Dashboard.md        # Status overview
└── Company_Handbook.md # Behavioral rules
```

---

## USAGE WORKFLOW

### Option A: Manual Processing (Recommended for Learning)

#### Step 1: Create a Task File

Drop a text file in the Inbox folder with your question or task:

```bash
echo "What is the difference between Docker and Kubernetes?" > ai_employee_vault/Inbox/question.txt
```

#### Step 2: Convert File to Task

Run the Python task creator:

```bash
python -c "
from pathlib import Path
from ai_employee.watcher.task_creator import TaskCreator

vault_path = Path('ai_employee_vault')
creator = TaskCreator(vault_path)
file_path = vault_path / 'Inbox' / 'question.txt'

if file_path.exists():
    task = creator.create_task_from_file(file_path)
    print(f'Task created: {task.id}')
else:
    print('File not found')
"
```

#### Step 3: Process with Claude Code

Claude Code will process the task through all 4 phases:

1. **Phase 1 - Task Ingestion:** Read task and handbook
2. **Phase 2 - Planning:** Generate execution plan
3. **Phase 3 - Execution:** Produce final answer
4. **Phase 4 - Finalization:** Move to Done folder

Run:
```bash
python claude_runner.py
```

Or interact with Claude Code directly in your session.

#### Step 4: View Results

Check the completed task:
```bash
cat ai_employee_vault/Done/task-*.md
```

Check the dashboard:
```bash
cat ai_employee_vault/Dashboard.md
```

---

### Option B: Automated Processing (With Watcher)

#### Step 1: Start the File Watcher (Terminal 1)

```bash
python -m ai_employee watch
```

This monitors the Inbox folder and automatically creates tasks from new files.

#### Step 2: Drop Files (Terminal 2)

```bash
echo "Explain machine learning in simple terms" > ai_employee_vault/Inbox/ml-question.txt
```

The watcher will automatically detect the file and create a task.

#### Step 3: Process Tasks (Terminal 2)

```bash
python claude_runner.py
```

Or interact with Claude Code directly to process pending tasks.

---

## EXAMPLE TASKS

### Example 1: Technical Question
```bash
echo "What are the benefits of microservices architecture?" > ai_employee_vault/Inbox/microservices.txt
```

### Example 2: Comparison Request
```bash
echo "Compare SQL and NoSQL databases with examples" > ai_employee_vault/Inbox/databases.txt
```

### Example 3: Explanation Request
```bash
echo "Explain how JWT authentication works" > ai_employee_vault/Inbox/jwt.txt
```

### Example 4: Summary Request
```bash
echo "Summarize the key principles of clean code" > ai_employee_vault/Inbox/clean-code.txt
```

---

## VIEWING RESULTS

### Check Dashboard
```bash
cat ai_employee_vault/Dashboard.md
```

Shows:
- Task counts (Inbox, Needs_Action, Done)
- Recent activity log

### View Completed Tasks
```bash
ls ai_employee_vault/Done/
cat ai_employee_vault/Done/task-*.md
```

Each completed task contains:
- Original question
- AI-generated plan (reference)
- **Final Answer** (the actual response)

### View Planning Artifacts
```bash
ls ai_employee_vault/Plans/
cat ai_employee_vault/Plans/plan-*.md
```

Shows the thinking process behind each answer.

---

## CUSTOMIZING BEHAVIOR

### Edit Company Handbook

```bash
nano ai_employee_vault/Company_Handbook.md
```

Add your own rules:
```markdown
# Company Handbook

## Rules
- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.
- [MEDIUM] Summaries under 200 words.
- [LOW] Use bullet points when possible.
- [CUSTOM] Always include code examples for technical topics.
```

The AI Employee will apply these rules when generating plans and answers.

---

## TROUBLESHOOTING

### No Tasks Being Created
- Check if files are in `ai_employee_vault/Inbox/`
- Verify the watcher is running: `python -m ai_employee watch`
- Manually create task using the Python command above

### Tasks Not Being Processed
- Ensure Claude Code is invoked (run `python claude_runner.py` or interact directly)
- Check `ai_employee_vault/Needs_Action/` for pending tasks

### View Logs
```bash
tail -f ai_employee_vault/activity.log
```

---

## COMMANDS REFERENCE

### Initialize Vault
```bash
python -m ai_employee init [--vault-path PATH]
```

### Start File Watcher
```bash
python -m ai_employee watch [--vault-path PATH]
```

### Show Configuration
```bash
python -m ai_employee config --show
```

### Process Tasks (via Claude Code)
```bash
python claude_runner.py
```

Or interact with Claude Code directly in this session.

---

## FOLDER STRUCTURE

```
ai_employee_vault/
├── Inbox/              # Drop files here (monitored by watcher)
├── Needs_Action/       # Tasks waiting for Claude Code processing
├── Done/               # Completed tasks with final answers
├── Plans/              # Planning artifacts (thinking process)
├── Dashboard.md        # Status overview
├── Company_Handbook.md # Behavioral rules
└── activity.log        # System log
```

---

## WORKFLOW SUMMARY

1. **Create Task:** Drop file in Inbox OR manually create task
2. **Process Task:** Claude Code reads, plans, executes, and produces answer
3. **View Results:** Check Done folder for completed tasks with answers
4. **Repeat:** System is ready for next task

---

## KEY FEATURES

✅ **Real AI Reasoning:** Claude Code generates contextual answers, not templates
✅ **Full Lifecycle:** Planning + Execution + Final Answer
✅ **Handbook-Guided:** Follows custom rules you define
✅ **Transparent:** Plans saved separately for review
✅ **Safe:** Original files preserved in Inbox
✅ **Local:** No external APIs required

---

## NEXT STEPS

1. Try the examples above
2. Customize the Company Handbook
3. Create your own tasks
4. Review the Plans folder to see the thinking process
5. Check Done folder for final answers

The AI Employee is ready to work! 🎯
