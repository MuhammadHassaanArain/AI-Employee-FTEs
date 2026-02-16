# Bronze Tier Testing Instructions

## Prerequisites

1. Python 3.11+ installed
2. Anthropic API key ready
3. Terminal access

## Setup Steps

### 1. Install Dependencies

```bash
cd bronze-tier

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install package
pip install -e .
```

### 2. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Initialize Vault

```bash
python -m ai_employee init
```

**Expected Output:**
```
✓ Vault initialized at: ./ai_employee_vault
✓ Open in Obsidian: ./ai_employee_vault
```

**Verify:**
- `ai_employee_vault/` directory exists
- Contains folders: `Inbox/`, `Needs_Action/`, `Done/`
- Contains files: `Dashboard.md`, `Company_Handbook.md`

## Test 1: File Detection and Task Creation

### Run the System

```bash
python -m ai_employee run
```

**Expected Output:**
```
Starting AI Employee...
Vault: ai_employee_vault
Watching: ai_employee_vault\Inbox
Max iterations: 10
Press Ctrl+C to stop

✓ File watcher started
✓ Monitoring: ai_employee_vault\Inbox
✓ Dashboard: ai_employee_vault\Dashboard.md
✓ Processing tasks automatically
```

### Add Test File

In a **separate terminal** (keep the system running):

```bash
echo "Review the Q1 sales report and prepare a summary for the team meeting" > ai_employee_vault/Inbox/sales_task.txt
```

### Expected Behavior (within 60 seconds)

1. **Console Output:**
   - "New file detected: sales_task.txt"
   - "Successfully created task [task-id]"
   - "Generated plan with X steps"
   - "Moved task to Done"

2. **File System Changes:**
   - `Inbox/sales_task.txt` - original file remains
   - `Needs_Action/task-[uuid].md` - created, then moved to Done
   - `Done/task-[uuid].md` - final location with AI plan appended

3. **Dashboard Update:**
   - Open `ai_employee_vault/Dashboard.md`
   - Task counts updated
   - Activity log shows recent actions

### Verify Task File

Open `ai_employee_vault/Done/task-[uuid].md`:

**Expected Structure:**
```markdown
---
id: [uuid]
title: Review the Q1 sales report...
source_path: [path]
created_at: [timestamp]
status: done
original_filename: sales_task.txt
file_size: [bytes]
detected_at: [timestamp]
---

Review the Q1 sales report and prepare a summary for the team meeting

---

## AI Generated Plan

1. [Step 1]
2. [Step 2]
3. [Step 3]
...
```

## Test 2: Multiple Files

### Add Multiple Files

```bash
echo "Send invoice to client ABC for project XYZ" > ai_employee_vault/Inbox/invoice.txt
echo "Schedule team meeting for next week" > ai_employee_vault/Inbox/meeting.txt
echo "Update documentation for new API endpoints" > ai_employee_vault/Inbox/docs.txt
```

### Expected Behavior

- All 3 files detected within 60 seconds
- 3 tasks created in `Needs_Action/`
- All processed and moved to `Done/`
- Dashboard shows count: Done: 4 (including previous test)

## Test 3: Handbook Rules

### Verify Handbook

Open `ai_employee_vault/Company_Handbook.md`:

```markdown
# Company Handbook

## Rules
- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.
- [MEDIUM] Summaries under 200 words.
- [LOW] Use bullet points when possible.
```

### Test Email Rule

```bash
echo "Send urgent email to CEO about budget overrun" > ai_employee_vault/Inbox/urgent_email.txt
```

### Expected Behavior

- Task processed
- Plan includes approval checkpoint for email action
- Plan may include warnings about email sending

## Test 4: Dashboard Verification

Open `ai_employee_vault/Dashboard.md`:

**Expected Format:**
```markdown
# AI Employee Dashboard

## Task Counts
- Inbox: 0
- Needs_Action: 0
- Done: 5

## Activity Log

[timestamp] | file_detected | Detected new file: urgent_email.txt | success
[timestamp] | task_created | Created task: Send urgent email... | success
[timestamp] | plan_generated | Generated plan with 4 steps | success
[timestamp] | task_moved | Moved task to Done | success
...
```

## Test 5: Error Handling

### Test with Invalid File

```bash
# Create a very large file
python -c "print('x' * 10000000)" > ai_employee_vault/Inbox/large.txt
```

### Expected Behavior

- System continues running (doesn't crash)
- Error logged in activity log
- Other tasks continue processing

## Test 6: Stop and Restart

### Stop the System

Press `Ctrl+C` in the terminal running the AI Employee

**Expected Output:**
```
Shutting down gracefully...
✓ File watcher stopped
✓ All tasks saved
```

### Restart

```bash
python -m ai_employee run
```

**Expected Behavior:**
- System starts successfully
- Previous tasks remain in `Done/`
- Dashboard shows correct counts
- Ready to process new files

## Success Criteria Checklist

- [ ] Files detected within 60 seconds
- [ ] Tasks created with correct YAML metadata
- [ ] AI plans generated and appended to task files
- [ ] Tasks moved from Needs_Action to Done
- [ ] Original files in Inbox preserved (not deleted)
- [ ] Dashboard updates with accurate counts
- [ ] Activity log records all actions
- [ ] Handbook rules applied to plans
- [ ] System handles multiple files
- [ ] System recovers from errors gracefully
- [ ] System can be stopped and restarted

## Troubleshooting

### No files detected
- Verify files are in `ai_employee_vault/Inbox/`
- Check file permissions
- Look for errors in console output

### API errors
- Verify `ANTHROPIC_API_KEY` in `.env`
- Check API key is valid
- Ensure internet connection

### Plans not generated
- Check `ai_employee_vault/activity.log` for errors
- Verify Claude API is responding
- Check rate limits

## Clean Up

To reset for fresh testing:

```bash
# Stop the system (Ctrl+C)

# Remove vault
rm -rf ai_employee_vault

# Reinitialize
python -m ai_employee init
```

## Expected Performance

- File detection: < 60 seconds
- Plan generation: < 10 seconds per task
- 10 tasks processed: < 5 minutes total
- System uptime: 24+ hours without crashes
