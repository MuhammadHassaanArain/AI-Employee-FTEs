# QuickStart Guide - Silver Tier AI Employee

Get started in 5 minutes with simple copy-paste commands.

## Two Modes Available

**Automated Mode** (Fast, Pattern-Based)
- Uses rule-based reasoning
- Perfect for automation and demos
- Command: `python claude_runner.py`

**Claude Code Mode** (Real AI Reasoning)
- Uses Claude Code for intelligent analysis
- Best for complex tasks and quality output
- Command: `python claude_runner_with_ai.py` (inside Claude Code CLI)

See `CLAUDE_CODE_INTEGRATION.md` for detailed comparison.

---

## Step 1: Initialize the System

```bash
# Navigate to silver-tier directory
cd silver-tier

# Initialize the vault
python -m ai_employee init
```

**Expected Output:**
```
[OK] Vault initialized at: ./ai_employee_vault
```

---

## Step 2: Test the System (Empty Run)

**Automated Mode:**
```bash
# Run the complete workflow (pattern-based)
python claude_runner.py
```

**Claude Code Mode:**
```bash
# Inside Claude Code CLI
python claude_runner_with_ai.py
```

**Expected Output:**
```
Files captured:       0
Emails captured:      0
Tasks processed:      0
```

✓ System is working!

---

## Step 3: Create a Test Task

```bash
# Create a simple research task
echo "Research the top 3 AI automation tools in 2026 and create a summary report." > ai_employee_vault/Inbox/research-task.txt
```

---

## Step 4: Process the Task

```bash
# Run the workflow again
python claude_runner.py
```

**Expected Output:**
```
Files captured:       1
Tasks processed:      1
Tasks completed:      1
```

**Check Results:**
```bash
# View completed task
ls ai_employee_vault/Done/

# View generated plan
ls ai_employee_vault/Plans/
```

---

## Step 5: Test Approval Workflow

**Create a task that requires approval:**

```bash
# Create an email task (requires human approval)
cat > ai_employee_vault/Inbox/email-task.txt << 'EOF'
Send email to client@example.com

Subject: Project Update Q1 2026

Please send an email with the following update:
- Phase 1 completed successfully
- Phase 2 starting next week
- On track for March 15th delivery

Best regards,
AI Employee
EOF
```

**Run workflow:**
```bash
python claude_runner.py
```

**Expected Output:**
```
Files captured:       1
Tasks processed:      1
Tasks completed:      0  (waiting for approval)
```

**View approval request:**
```bash
# Check what's waiting for approval
ls ai_employee_vault/Waiting_Approval/

# Read the approval request
cat ai_employee_vault/Waiting_Approval/approval-*.md
```

**Approve the task:**
```bash
# Create approval file
echo "Approved by human" > ai_employee_vault/Waiting_Approval/APPROVED.txt
```

**Run workflow again:**
```bash
python claude_runner.py
```

**Expected Output:**
```
Approvals processed:  1
Tasks executed:       1
Tasks completed:      1
```

---

## Step 6: Run Automated Scheduler

**Single run (for testing):**
```bash
python scheduler.py --once
```

**Continuous mode (runs every 15 minutes):**
```bash
# Press Ctrl+C to stop
python scheduler.py
```

**Custom interval (every 5 minutes):**
```bash
python scheduler.py --interval 5
```

---

## Optional: Setup Gmail Monitoring

**Set environment variables:**

```bash
# Windows Command Prompt
set GMAIL_EMAIL=your-email@gmail.com
set GMAIL_PASSWORD=your-app-password

# Windows PowerShell
$env:GMAIL_EMAIL="your-email@gmail.com"
$env:GMAIL_PASSWORD="your-app-password"

# Linux/Mac
export GMAIL_EMAIL=your-email@gmail.com
export GMAIL_PASSWORD=your-app-password
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate new app password
3. Use that password (not your regular Gmail password)

**Test Gmail watcher:**
```bash
python -m ai_employee.watchers.gmail_watcher
```

---

## Optional: Setup Email Sending

**Set SMTP credentials:**

```bash
# Windows Command Prompt
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password

# Windows PowerShell
$env:SMTP_EMAIL="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
```

**Test email sending:**
```bash
python -m ai_employee.mcp.mcp_server
```

---

## Quick Commands Reference

```bash
# Initialize vault
python -m ai_employee init

# Run workflow once
python claude_runner.py

# Run scheduler (continuous)
python scheduler.py

# Run scheduler (single run)
python scheduler.py --once

# Test Gmail watcher
python -m ai_employee.watchers.gmail_watcher

# Test MCP server
python -m ai_employee.mcp.mcp_server

# View activity log
tail -50 ai_employee_vault/activity.log

# Check vault status
ls ai_employee_vault/Done/
ls ai_employee_vault/Plans/
ls ai_employee_vault/Waiting_Approval/
```

---

## Vault Folder Structure

```
ai_employee_vault/
├── Inbox/              # Drop files here
├── Needs_Action/       # Tasks being processed
├── Waiting_Approval/   # Tasks awaiting approval
├── Approved/           # Approved tasks
├── Rejected/           # Rejected tasks
├── Done/               # Completed tasks
├── Plans/              # Generated plans
├── LinkedIn_Posts/     # Queued LinkedIn posts
└── activity.log        # System log
```

---

## Troubleshooting

**Vault not found:**
```bash
python -m ai_employee init
```

**No tasks to process:**
```bash
echo "Test task" > ai_employee_vault/Inbox/test.txt
python claude_runner.py
```

**Gmail not working:**
```bash
# Check credentials are set
echo %GMAIL_EMAIL%        # Windows CMD
echo $env:GMAIL_EMAIL     # Windows PowerShell
echo $GMAIL_EMAIL         # Linux/Mac
```

**View errors:**
```bash
tail -50 ai_employee_vault/activity.log
```

---

## Demo Script (5 Minutes)

```bash
# 1. Initialize
python -m ai_employee init

# 2. Create test tasks
echo "Research AI automation tools" > ai_employee_vault/Inbox/research.txt
echo "Send email to demo@example.com with update" > ai_employee_vault/Inbox/email.txt

# 3. Run workflow
python claude_runner.py

# 4. Check results
ls ai_employee_vault/Done/
ls ai_employee_vault/Waiting_Approval/

# 5. Approve email task
echo "Approved" > ai_employee_vault/Waiting_Approval/APPROVED.txt

# 6. Run workflow again
python claude_runner.py

# 7. Verify all tasks completed
ls ai_employee_vault/Done/
```

---

## Windows Task Scheduler Setup

**Quick Setup:**

1. Open Task Scheduler: `Win + R` → `taskschd.msc`
2. Create Basic Task → Name: `AI Employee`
3. Trigger: Daily, repeat every 15 minutes
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `scheduler.py --once`
   - Start in: `<path-to-silver-tier-folder>`
5. Test: Right-click task → Run

**Detailed instructions:** See `SCHEDULER_SETUP.md`

---

## Next Steps

1. ✓ Run the QuickStart commands above
2. ✓ Test with your own tasks
3. ✓ Configure Gmail (optional)
4. ✓ Configure SMTP (optional)
5. ✓ Setup Task Scheduler for automation

**System is ready to use!**

For detailed documentation, see:
- `SILVER_TIER_SUMMARY.md` - Complete implementation overview
- `SCHEDULER_SETUP.md` - Detailed scheduler setup
- `TECHNICAL_REVIEW_REPORT.md` - Technical audit results

---

**Questions?** Check the activity log: `ai_employee_vault/activity.log`
