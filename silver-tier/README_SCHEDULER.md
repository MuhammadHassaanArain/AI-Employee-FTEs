# AI Employee Silver Tier - Scheduler Setup Guide

## Overview

The AI Employee uses **OS-level scheduling** (Windows Task Scheduler) to run automatically every 15 minutes.

This is NOT application-level scheduling (no Python `schedule` library).
The task survives system reboots and runs whether you're logged in or not.

## Quick Setup

### 1. Prerequisites

- Python 3.8+ installed
- Project dependencies installed: `pip install -r requirements.txt`
- Vault initialized: `python -m ai_employee init`
- LinkedIn OAuth configured (if using LinkedIn posting)

### 2. Create Scheduled Task

Open PowerShell as Administrator and run:

```powershell
cd path\to\silver-tier
.\scripts\setup_windows_scheduler.ps1
```

This will:
- Create a Windows Task Scheduler task named `AI-Employee-Silver`
- Schedule it to run every 15 minutes
- Configure it to run whether user is logged in or not
- Set it to start automatically after system reboot
- Create logs directory at `logs/scheduler.log`

### 3. Verify Setup

Check that the task was created:

```powershell
Get-ScheduledTask -TaskName "AI-Employee-Silver"
```

You should see:
```
TaskPath  TaskName              State
--------  --------              -----
\         AI-Employee-Silver    Ready
```

### 4. Test Run

Run the task manually to verify it works:

```powershell
Start-ScheduledTask -TaskName "AI-Employee-Silver"
```

Check the logs:

```powershell
Get-Content logs\scheduler.log -Tail 50
```

## Configuration

### Change Interval

To run every 30 minutes instead of 15:

```powershell
.\scripts\setup_windows_scheduler.ps1 -IntervalMinutes 30
```

### Custom Python Path

If Python is not in your PATH:

```powershell
.\scripts\setup_windows_scheduler.ps1 -PythonPath "C:\Python39\python.exe"
```

## Monitoring

### View Task Status

```powershell
Get-ScheduledTask -TaskName "AI-Employee-Silver" | Get-ScheduledTaskInfo
```

### View Logs

```powershell
# Last 50 lines
Get-Content logs\scheduler.log -Tail 50

# Follow logs in real-time
Get-Content logs\scheduler.log -Wait -Tail 10
```

### View Task History

1. Open Task Scheduler GUI: `taskschd.msc`
2. Navigate to Task Scheduler Library
3. Find `AI-Employee-Silver`
4. Click "History" tab

## Troubleshooting

### Task Not Running

1. Check task status:
   ```powershell
   Get-ScheduledTask -TaskName "AI-Employee-Silver"
   ```

2. Check last run result:
   ```powershell
   Get-ScheduledTask -TaskName "AI-Employee-Silver" | Get-ScheduledTaskInfo
   ```

3. Run manually to see errors:
   ```powershell
   Start-ScheduledTask -TaskName "AI-Employee-Silver"
   ```

### Permission Issues

The task runs with your user account. Ensure:
- You have read/write access to the project directory
- You have read/write access to the vault directory
- Python can access environment variables (`.env` file)

### Python Not Found

If you get "Python not found" errors:

1. Find your Python path:
   ```powershell
   Get-Command python | Select-Object -ExpandProperty Source
   ```

2. Recreate task with explicit path:
   ```powershell
   .\scripts\setup_windows_scheduler.ps1 -PythonPath "C:\Path\To\python.exe"
   ```

## Removal

To remove the scheduled task:

```powershell
.\scripts\remove_scheduler.ps1
```

Or manually:

```powershell
Unregister-ScheduledTask -TaskName "AI-Employee-Silver" -Confirm:$false
```

## What the Scheduler Does

Every 15 minutes, the task runs:

```bash
python -m ai_employee.runner
```

This executes the full workflow:

1. **Capture Inputs**
   - File watcher scans `Inbox/` for new files
   - Gmail watcher checks for new emails

2. **Generate Plans**
   - Reasoning skill analyzes each task
   - Creates `Plan.md` files
   - Routes to approval or done

3. **Process Approvals**
   - Checks for `APPROVED.txt` or `REJECTED.txt`
   - Moves approved tasks to execution queue

4. **Execute Actions**
   - Posts to LinkedIn via real API
   - Sends emails via MCP
   - Moves completed tasks to `Done/`

All output is logged to `logs/scheduler.log`.

## Advanced Configuration

### Run on Different Schedule

Edit the task in Task Scheduler GUI:
1. Open `taskschd.msc`
2. Find `AI-Employee-Silver`
3. Right-click → Properties
4. Go to Triggers tab
5. Edit the trigger

### Run Only During Business Hours

Add a condition:
1. Open task properties
2. Go to Conditions tab
3. Check "Start only if the computer is on AC power"
4. Or add time-based conditions

### Email Notifications on Failure

1. Open task properties
2. Go to Actions tab
3. Add new action: "Send an email"
4. Configure SMTP settings

## Verification Checklist

After setup, verify:

- [ ] Task exists: `Get-ScheduledTask -TaskName "AI-Employee-Silver"`
- [ ] Task is enabled (State = Ready)
- [ ] Task runs successfully: `Start-ScheduledTask -TaskName "AI-Employee-Silver"`
- [ ] Logs are created: `logs/scheduler.log` exists
- [ ] Workflow completes without errors
- [ ] Tasks are processed automatically
- [ ] LinkedIn posts work (if configured)
- [ ] Approvals are processed correctly

## Support

If you encounter issues:

1. Check logs: `logs/scheduler.log`
2. Run manually: `python -m ai_employee.runner`
3. Check Task Scheduler event logs
4. Verify Python and dependencies are installed
5. Verify `.env` configuration is correct
