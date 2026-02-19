# Windows Task Scheduler Setup Guide

## Overview

The AI Employee scheduler can run in two modes:
1. **Continuous Mode**: Python script runs continuously and schedules tasks internally
2. **Task Scheduler Mode**: Windows Task Scheduler runs the script periodically

## Option 1: Continuous Mode (Recommended for Development)

Run the scheduler continuously in a terminal:

```bash
# Run every 15 minutes (default)
python scheduler.py

# Run every 30 minutes
python scheduler.py --interval 30

# Run every 5 minutes
python scheduler.py --interval 5
```

Press `Ctrl+C` to stop.

## Option 2: Windows Task Scheduler (Recommended for Production)

### Step-by-Step Setup

#### 1. Open Task Scheduler
- Press `Win + R`
- Type `taskschd.msc`
- Press Enter

#### 2. Create Basic Task
- Click "Create Basic Task" in the right panel
- Name: `AI Employee - Silver Tier`
- Description: `Runs AI Employee workflow every 15 minutes`
- Click "Next"

#### 3. Set Trigger
- Select "Daily"
- Click "Next"
- Set start date and time (e.g., today at 9:00 AM)
- Click "Next"

#### 4. Set Action
- Select "Start a program"
- Click "Next"

#### 5. Configure Program
- **Program/script**: `python.exe`
  - Or full path: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe`
  - To find Python path: `where python` in Command Prompt

- **Add arguments**: `scheduler.py --once`

- **Start in**: `D:\Hassaan_Work\GIAIC\Quarter-04\Hackathons\hackathon-0\AI-Employee-FTEs\silver-tier`
  - Use your actual path to the silver-tier folder

- Click "Next"

#### 6. Review and Finish
- Check "Open the Properties dialog for this task when I click Finish"
- Click "Finish"

#### 7. Configure Advanced Settings
In the Properties dialog:

**General Tab:**
- Check "Run whether user is logged on or not"
- Check "Run with highest privileges"

**Triggers Tab:**
- Edit the trigger
- Check "Repeat task every: 15 minutes"
- For a duration of: "Indefinitely"
- Click "OK"

**Settings Tab:**
- Uncheck "Stop the task if it runs longer than: 3 days"
- Check "Run task as soon as possible after a scheduled start is missed"
- Check "If the task fails, restart every: 1 minute"
- Attempt to restart up to: 3 times

Click "OK" to save.

#### 8. Test the Task
- Right-click the task in Task Scheduler
- Click "Run"
- Check the "Last Run Result" column (should show "0x0" for success)

### Viewing Logs

Task Scheduler logs are stored in:
```
ai_employee_vault/activity.log
```

To view recent activity:
```bash
# View last 50 lines
tail -n 50 ai_employee_vault/activity.log

# Or on Windows PowerShell
Get-Content ai_employee_vault/activity.log -Tail 50
```

### Troubleshooting

#### Task doesn't run
1. Check "Last Run Result" in Task Scheduler
2. Verify Python path is correct: `where python`
3. Verify working directory path is correct
4. Check that vault exists: `python -m ai_employee init`

#### Task runs but fails
1. Check activity.log for errors
2. Run manually to see errors: `python scheduler.py --once`
3. Verify all dependencies installed: `pip install -r requirements.txt`

#### Gmail not working
1. Set environment variables in Task Scheduler:
   - In Properties → Actions → Edit
   - Add to "Add arguments": `--vault-path ./ai_employee_vault`
   - Or set system environment variables:
     - `GMAIL_EMAIL=your-email@gmail.com`
     - `GMAIL_PASSWORD=your-app-password`

## Environment Variables for Task Scheduler

To set environment variables for the scheduled task:

### Method 1: System Environment Variables
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab
3. Click "Environment Variables"
4. Under "System variables", click "New"
5. Add:
   - `GMAIL_EMAIL` = `your-email@gmail.com`
   - `GMAIL_PASSWORD` = `your-app-password`
   - `SMTP_EMAIL` = `your-email@gmail.com`
   - `SMTP_PASSWORD` = `your-app-password`

### Method 2: Batch File Wrapper
Create `run_scheduler.bat`:

```batch
@echo off
set GMAIL_EMAIL=your-email@gmail.com
set GMAIL_PASSWORD=your-app-password
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password

cd /d "D:\Hassaan_Work\GIAIC\Quarter-04\Hackathons\hackathon-0\AI-Employee-FTEs\silver-tier"
python scheduler.py --once
```

Then in Task Scheduler:
- Program/script: `run_scheduler.bat`
- Start in: (leave empty)

## Monitoring

### Check if scheduler is running
```bash
# Continuous mode
# Look for python.exe process running scheduler.py

# Task Scheduler mode
# Open Task Scheduler and check "Status" column
```

### View statistics
```bash
# Run once to see summary
python scheduler.py --once
```

### Stop scheduler
```bash
# Continuous mode
# Press Ctrl+C in the terminal

# Task Scheduler mode
# Open Task Scheduler
# Right-click task → Disable
```

## Recommended Schedule

- **Development**: Every 5-15 minutes (continuous mode)
- **Production**: Every 15-30 minutes (Task Scheduler)
- **High-volume**: Every 5 minutes (Task Scheduler)

## Notes

- The scheduler runs the complete workflow each time:
  1. Check Inbox/ for new files
  2. Check Gmail for new emails
  3. Process tasks with reasoning skill
  4. Process pending approvals
  5. Execute approved tasks via MCP server
  6. Mark tasks as Done

- Each run is independent and stateless
- Safe to run multiple times (idempotent)
- No data loss if scheduler is stopped
