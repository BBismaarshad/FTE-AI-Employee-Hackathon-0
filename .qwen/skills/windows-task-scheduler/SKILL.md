# Windows Task Scheduler Integration

Schedule AI Employee tasks using Windows Task Scheduler.

## Overview

This skill provides scripts and configurations to schedule AI Employee operations using Windows Task Scheduler. It enables automated, recurring execution of watchers, orchestrator cycles, and scheduled tasks like daily briefings.

## Features

- **Automated Scheduling**: Set up recurring tasks without manual intervention
- **Multiple Task Types**: Support for watchers, orchestrator, and custom scripts
- **Startup Tasks**: Launch AI Employee on system boot
- **Error Handling**: Tasks log failures and can send notifications
- **Easy Setup**: PowerShell scripts for quick configuration
- **Management Tools**: View, enable, disable, and remove scheduled tasks

## Prerequisites

- Windows 10/11
- Administrator access (for task creation)
- Python and all dependencies installed
- AI Employee vault configured

## Available Scheduled Tasks

### 1. Orchestrator Cycle
Runs the main orchestrator to process pending actions.

**Default Schedule**: Every 5 minutes
**Purpose**: Process action files in Needs_Action folder

### 2. Gmail Watcher
Monitors Gmail for new unread emails.

**Default Schedule**: Every 2 minutes
**Purpose**: Create action files for new emails

### 3. WhatsApp Watcher
Monitors WhatsApp Web for keyword messages.

**Default Schedule**: Every 1 minute
**Purpose**: Create action files for urgent WhatsApp messages
**Note**: Requires graphical session (won't work on locked screen)

### 4. Filesystem Watcher
Monitors drop folder for new files.

**Default Schedule**: Every 30 seconds
**Purpose**: Create action files for dropped files

### 5. Daily Briefing
Generates Monday Morning CEO Briefing.

**Default Schedule**: Daily at 7:00 AM
**Purpose**: Create daily summary and insights

### 6. Weekly Audit
Comprehensive weekly review of all activities.

**Default Schedule**: Sunday at 10:00 PM
**Purpose**: Generate weekly business report

## Setup Scripts

### Quick Setup (All Tasks)
```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File skills\setup_tasks.ps1
```

### Individual Task Setup
```powershell
# Setup orchestrator task
powershell -File skills\task_scheduler.ps1 -Task "orchestrator" -Action "create"

# Setup Gmail watcher
powershell -File skills\task_scheduler.ps1 -Task "gmail_watcher" -Action "create"

# Setup daily briefing
powershell -File skills\task_scheduler.ps1 -Task "daily_briefing" -Action "create"
```

## Task Management

### View All Tasks
```powershell
powershell -File skills\task_scheduler.ps1 -Action "list"
```

### Disable Task
```powershell
powershell -File skills\task_scheduler.ps1 -Task "whatsapp_watcher" -Action "disable"
```

### Enable Task
```powershell
powershell -File skills\task_scheduler.ps1 -Task "whatsapp_watcher" -Action "enable"
```

### Remove Task
```powershell
powershell -File skills\task_scheduler.ps1 -Task "old_task" -Action "remove"
```

## Task Configuration

### Customize Schedules

Edit `task_config.json` to customize task schedules:

```json
{
  "orchestrator": {
    "enabled": true,
    "interval_minutes": 5,
    "description": "Process pending AI Employee actions"
  },
  "gmail_watcher": {
    "enabled": true,
    "interval_minutes": 2,
    "description": "Monitor Gmail for unread emails"
  },
  "whatsapp_watcher": {
    "enabled": false,
    "interval_minutes": 1,
    "description": "Monitor WhatsApp for urgent messages",
    "note": "Requires active graphical session"
  },
  "filesystem_watcher": {
    "enabled": true,
    "interval_minutes": 0.5,
    "description": "Monitor drop folder for files"
  },
  "daily_briefing": {
    "enabled": true,
    "time": "07:00",
    "description": "Generate daily CEO briefing"
  },
  "weekly_audit": {
    "enabled": true,
    "day": "Sunday",
    "time": "22:00",
    "description": "Generate weekly business audit"
  }
}
```

## Task Scheduler XML Templates

Each task is created using Windows Task Scheduler XML definitions.

### Orchestrator Task
```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>AI Employee Orchestrator - Process pending actions</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT5M</Interval>
      </Repetition>
      <StartBoundary>2026-04-06T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>orchestrator.py --vault "C:\path\to\AI_Employee_Vault" --once</Arguments>
      <WorkingDirectory>C:\path\to\FTE-AI-Employee-Hackathon-0</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

## Usage Examples

### Example 1: Setup All Tasks
```powershell
# Navigate to project directory
cd C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0

# Run setup script
powershell -ExecutionPolicy Bypass -File skills\setup_tasks.ps1

# Verify tasks created
powershell -File skills\task_scheduler.ps1 -Action "list"
```

### Example 2: Custom Configuration
```powershell
# Edit task_config.json first
notepad skills\task_config.json

# Apply configuration
powershell -File skills\task_scheduler.ps1 -Action "apply-config"
```

### Example 3: Monitor Task Execution
```powershell
# View task history in Event Viewer
eventvwr.msc

# Navigate to:
# Application and Services Logs
#   -> Microsoft
#     -> Windows
#       -> TaskScheduler
#         -> Operational
```

## Troubleshooting

### Tasks Not Running
1. **Check Task Status**:
   ```powershell
   Get-ScheduledTask -TaskName "AI Employee*"
   ```

2. **View Task History**:
   ```powershell
   Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" |
     Where-Object {$_.Message -like "*AI Employee*"} |
     Select-Object -First 20
   ```

3. **Check Python Path**: Ensure Python is in system PATH

4. **Verify Working Directory**: Task must run from project directory

### Permission Issues
- Run setup as Administrator
- Check execution policy: `Get-ExecutionPolicy`
- Set if needed: `Set-ExecutionPolicy RemoteSigned`

### WhatsApp Watcher Not Working
- Task requires active user session
- Won't work on locked screen
- Consider running manually instead of scheduled

## Best Practices

1. **Start Conservatively**: Begin with longer intervals, reduce as needed
2. **Monitor Logs**: Check task execution logs regularly
3. **Don't Over-Schedule**: Avoid running too many tasks simultaneously
4. **Test First**: Run tasks manually before scheduling
5. **Document Changes**: Keep track of schedule modifications
6. **Review Weekly**: Check if tasks are actually needed at current frequency

## Integration with Orchestrator

Scheduled tasks work with the main orchestrator:

1. **Watchers**: Create action files in Needs_Action/
2. **Orchestrator**: Processes pending actions (runs every 5 min)
3. **Briefings**: Generate periodic reports
4. **Audits**: Comprehensive reviews

## Alternative: Simple Batch File

For simple setups, use a batch file instead of Task Scheduler:

```batch
@echo off
:start
python orchestrator.py --vault "C:\path\to\AI_Employee_Vault" --once
timeout /t 300 /nobreak
goto start
```

Run this batch file in a hidden window:
```powershell
Start-Process -WindowStyle Hidden -FilePath "start_monitoring.bat"
```

## Next Steps (Gold Tier Enhancements)

- Email notifications on task failures
- Task execution dashboard
- Dynamic scheduling based on activity levels
- Cloud VM task scheduling
- Cross-machine task synchronization
- Task performance analytics
