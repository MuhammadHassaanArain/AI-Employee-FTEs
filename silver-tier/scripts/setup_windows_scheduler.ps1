# AI Employee Silver Tier - Windows Task Scheduler Setup
# This script creates an OS-level scheduled task that runs every 15 minutes

param(
    [string]$ProjectPath = $PSScriptRoot + "\..",
    [string]$PythonPath = "python",
    [int]$IntervalMinutes = 15
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Employee - Windows Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Resolve absolute paths
$ProjectPath = Resolve-Path $ProjectPath
$LogDir = Join-Path $ProjectPath "logs"
$LogFile = Join-Path $LogDir "scheduler.log"

# Create logs directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "[OK] Created logs directory: $LogDir" -ForegroundColor Green
}

# Verify Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found at: $PythonPath" -ForegroundColor Red
    Write-Host "Please install Python or specify correct path with -PythonPath parameter" -ForegroundColor Red
    exit 1
}

# Verify project structure
$runnerPath = Join-Path $ProjectPath "ai_employee\runner.py"
if (-not (Test-Path $runnerPath)) {
    Write-Host "[ERROR] Runner not found at: $runnerPath" -ForegroundColor Red
    Write-Host "Please ensure you're running this script from the project root" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Runner found: $runnerPath" -ForegroundColor Green

# Task configuration
$TaskName = "AI-Employee-Silver"
$TaskDescription = "AI Employee Silver Tier - Automated workflow runner"
$TaskAction = "$PythonPath -m ai_employee.runner"

Write-Host ""
Write-Host "Task Configuration:" -ForegroundColor Cyan
Write-Host "  Name:        $TaskName" -ForegroundColor White
Write-Host "  Interval:    Every $IntervalMinutes minutes" -ForegroundColor White
Write-Host "  Action:      $TaskAction" -ForegroundColor White
Write-Host "  Working Dir: $ProjectPath" -ForegroundColor White
Write-Host "  Log File:    $LogFile" -ForegroundColor White
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "[WARNING] Task '$TaskName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to replace it? (y/n)"
    if ($response -ne "y") {
        Write-Host "Setup cancelled" -ForegroundColor Yellow
        exit 0
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[OK] Removed existing task" -ForegroundColor Green
}

# Create scheduled task action
$action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "-m ai_employee.runner" `
    -WorkingDirectory $ProjectPath

# Create trigger (every N minutes)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Create principal (run whether user is logged on or not)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null

    Write-Host ""
    Write-Host "[SUCCESS] Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  - Runs every $IntervalMinutes minutes" -ForegroundColor White
    Write-Host "  - Starts automatically after system reboot" -ForegroundColor White
    Write-Host "  - Runs whether user is logged in or not" -ForegroundColor White
    Write-Host "  - Logs output to: $LogFile" -ForegroundColor White
    Write-Host ""
    Write-Host "Verification Commands:" -ForegroundColor Cyan
    Write-Host "  View task:   Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  Run now:     Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  View logs:   Get-Content '$LogFile' -Tail 50" -ForegroundColor White
    Write-Host "  Remove task: .\scripts\remove_scheduler.ps1" -ForegroundColor White
    Write-Host ""

    # Ask if user wants to run the task now
    $runNow = Read-Host "Do you want to run the task now for testing? (y/n)"
    if ($runNow -eq "y") {
        Write-Host "Starting task..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2
        Write-Host "[OK] Task started. Check logs for output." -ForegroundColor Green
    }

} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
