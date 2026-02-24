# AI Employee Silver Tier - Remove Windows Task Scheduler
# This script removes the scheduled task

param(
    [string]$TaskName = "AI-Employee-Silver"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Employee - Remove Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if (-not $existingTask) {
    Write-Host "[INFO] Task '$TaskName' does not exist" -ForegroundColor Yellow
    Write-Host "Nothing to remove." -ForegroundColor White
    exit 0
}

Write-Host "Found task: $TaskName" -ForegroundColor White
Write-Host ""

# Confirm removal
$response = Read-Host "Are you sure you want to remove this task? (y/n)"
if ($response -ne "y") {
    Write-Host "Removal cancelled" -ForegroundColor Yellow
    exit 0
}

# Remove the task
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host ""
    Write-Host "[SUCCESS] Task '$TaskName' removed successfully!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to remove task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Removal Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
