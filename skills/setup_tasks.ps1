# Windows Task Scheduler Setup Script for AI Employee
# Run as Administrator

param(
    [switch]$All,
    [string]$Task = "",
    [string]$Action = "create"
)

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VaultPath = Join-Path $ProjectRoot "AI_Employee_Vault"
$PythonExe = "python"

# Ensure running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator!"
    exit 1
}

function Get-TaskConfig {
    return @{
        orchestrator = @{
            Name = "AI Employee - Orchestrator"
            Description = "Process pending AI Employee actions every 5 minutes"
            Interval = "PT5M"  # 5 minutes
            Script = "orchestrator.py"
            Arguments = "--vault `"$VaultPath`" --once"
        }
        gmail_watcher = @{
            Name = "AI Employee - Gmail Watcher"
            Description = "Monitor Gmail for unread emails every 2 minutes"
            Interval = "PT2M"  # 2 minutes
            Script = "watchers\gmail_watcher.py"
            Arguments = "--vault `"$VaultPath`" --once"
        }
        whatsapp_watcher = @{
            Name = "AI Employee - WhatsApp Watcher"
            Description = "Monitor WhatsApp for urgent messages every 1 minute"
            Interval = "PT1M"  # 1 minute
            Script = "watchers\whatsapp_watcher.py"
            Arguments = "--vault `"$VaultPath`" --once"
        }
        filesystem_watcher = @{
            Name = "AI Employee - Filesystem Watcher"
            Description = "Monitor drop folder for files every 30 seconds"
            Interval = "PT30S"  # 30 seconds
            Script = "watchers\filesystem_watcher.py"
            Arguments = "--vault `"$VaultPath`" --once"
        }
        daily_briefing = @{
            Name = "AI Employee - Daily Briefing"
            Description = "Generate daily CEO briefing at 7:00 AM"
            Time = "07:00"
            Script = "orchestrator.py"
            Arguments = "--vault `"$VaultPath`" --briefing"
        }
        weekly_audit = @{
            Name = "AI Employee - Weekly Audit"
            Description = "Generate weekly business audit on Sunday at 10:00 PM"
            Day = "Sunday"
            Time = "22:00"
            Script = "orchestrator.py"
            Arguments = "--vault `"$VaultPath`" --weekly-audit"
        }
    }
}

function Create-ScheduledTask($taskKey, $config) {
    $taskName = $config.Name
    
    # Check if task already exists
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Task already exists: $taskName" -ForegroundColor Yellow
        $response = Read-Host "Overwrite? (y/n)"
        if ($response -ne 'y') {
            return
        }
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # Create trigger
    if ($config.Interval) {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $(
            if ($config.Interval -match 'PT(\d+)M') { $matches[1] }
            elseif ($config.Interval -match 'PT(\d+)S') { $matches[1] / 60 }
            else { 5 }
        ))
    }
    elseif ($config.Time) {
        if ($config.Day) {
            $trigger = New-ScheduledTaskTrigger -Daily -At $config.Time -DaysOfWeek $config.Day
        }
        else {
            $trigger = New-ScheduledTaskTrigger -Daily -At $config.Time
        }
    }

    # Create action
    $action = New-ScheduledTaskAction -Execute $PythonExe `
        -Argument "$($config.Arguments)" `
        -WorkingDirectory $ProjectRoot

    # Create settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    # Register task
    try {
        Register-ScheduledTask -TaskName $taskName `
            -Trigger $trigger `
            -Action $action `
            -Settings $settings `
            -Description $config.Description `
            -ErrorAction Stop
        
        Write-Host "✓ Task created: $taskName" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to create task: $taskName" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

function Remove-ScheduledTask($taskKey, $config) {
    $taskName = $config.Name
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($existing) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "✓ Task removed: $taskName" -ForegroundColor Green
    }
    else {
        Write-Host "Task not found: $taskName" -ForegroundColor Yellow
    }
}

function List-AllTasks {
    $tasks = Get-ScheduledTask -TaskName "AI Employee*" -ErrorAction SilentlyContinue
    
    if (-not $tasks) {
        Write-Host "No AI Employee tasks found." -ForegroundColor Yellow
        return
    }

    Write-Host "`nAI Employee Scheduled Tasks:" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    foreach ($task in $tasks) {
        $state = $task.State
        $color = if ($state -eq 'Ready') { 'Green' } else { 'Yellow' }
        Write-Host "  $($task.TaskName)" -ForegroundColor White
        Write-Host "    State: $state" -ForegroundColor $color
        Write-Host "    Description: $($task.Description)" -ForegroundColor Gray
        Write-Host ""
    }
}

# Main execution
$taskConfigs = Get-TaskConfig

if ($All) {
    Write-Host "`nSetting up all AI Employee scheduled tasks..." -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    foreach ($key in $taskConfigs.Keys) {
        Create-ScheduledTask $key $taskConfigs[$key]
    }
    
    Write-Host "`n✓ All tasks setup complete!" -ForegroundColor Green
    Write-Host "Use 'schtasks /query | findstr `"AI Employee`"' to view tasks" -ForegroundColor Gray
}
elseif ($Task) {
    if ($taskConfigs.ContainsKey($Task)) {
        $config = $taskConfigs[$Task]
        
        switch ($Action) {
            "create" { Create-ScheduledTask $Task $config }
            "remove" { Remove-ScheduledTask $Task $config }
            "disable" {
                Disable-ScheduledTask -TaskName $config.Name -ErrorAction SilentlyContinue
                Write-Host "✓ Task disabled: $($config.Name)" -ForegroundColor Green
            }
            "enable" {
                Enable-ScheduledTask -TaskName $config.Name -ErrorAction SilentlyContinue
                Write-Host "✓ Task enabled: $($config.Name)" -ForegroundColor Green
            }
            default { Write-Host "Unknown action: $Action" -ForegroundColor Red }
        }
    }
    else {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host "Available tasks: $($taskConfigs.Keys -join ', ')" -ForegroundColor Yellow
    }
}
elseif ($Action -eq "list") {
    List-AllTasks
}
else {
    Write-Host "`nAI Employee Task Scheduler Setup" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\setup_tasks.ps1 -All                    # Setup all tasks"
    Write-Host "  .\setup_tasks.ps1 -Task orchestrator      # Setup specific task"
    Write-Host "  .\setup_tasks.ps1 -Action list            # List all tasks"
    Write-Host ""
    Write-Host "Available Tasks:" -ForegroundColor White
    foreach ($key in $taskConfigs.Keys) {
        Write-Host "  $key - $($taskConfigs[$key].Description)" -ForegroundColor Gray
    }
}
