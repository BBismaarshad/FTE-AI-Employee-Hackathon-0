# Windows Task Scheduler Skill

Automate AI Employee tasks using Windows Task Scheduler for 24/7 operation.

## Overview

The Windows Task Scheduler setup script configures automated running of all AI Employee watchers and the orchestrator on a schedule. This enables your AI Employee to work autonomously without manual intervention.

## Scheduled Tasks

### Core Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| **Orchestrator** | Every 5 minutes | Process pending action files |
| **Gmail Watcher** | Every 2 minutes | Monitor for unread emails |
| **WhatsApp Watcher** | Every 1 minute | Monitor for urgent messages |
| **Filesystem Watcher** | Every 30 seconds | Monitor drop folder |

### Reporting Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| **Daily Briefing** | 7:00 AM daily | Generate CEO briefing |
| **Weekly Audit** | Sunday 10:00 PM | Generate weekly business audit |

## Setup Instructions

### 1. Open PowerShell as Administrator

Right-click PowerShell and select **"Run as Administrator"**

### 2. Navigate to Project Directory

```powershell
cd C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0
```

### 3. Run Setup Script

```powershell
powershell -ExecutionPolicy Bypass -File skills\setup_tasks.ps1 -All
```

This creates all scheduled tasks automatically.

### 4. Verify Tasks

```powershell
powershell -File skills\setup_tasks.ps1 -Action list
```

## Individual Task Management

### Create Specific Task

```powershell
powershell -File skills\setup_tasks.ps1 -Task gmail_watcher
```

### Remove Specific Task

```powershell
powershell -File skills\setup_tasks.ps1 -Task gmail_watcher -Action remove
```

### Enable/Disable Task

```powershell
# Disable temporarily
powershell -File skills\setup_tasks.ps1 -Task gmail_watcher -Action disable

# Re-enable
powershell -File skills\setup_tasks.ps1 -Task gmail_watcher -Action enable
```

## Task Details

### Orchestrator
- **Script**: `orchestrator.py`
- **Arguments**: `--vault "AI_Employee_Vault" --once`
- **Runs**: Every 5 minutes
- **Purpose**: Processes all pending action files in `Needs_Action/`

### Gmail Watcher
- **Script**: `watchers/gmail_watcher.py`
- **Arguments**: `--vault "AI_Employee_Vault" --once`
- **Runs**: Every 2 minutes
- **Purpose**: Checks for new unread emails

### WhatsApp Watcher
- **Script**: `watchers/whatsapp_watcher.py`
- **Arguments**: `--vault "AI_Employee_Vault" --once`
- **Runs**: Every 1 minute
- **Purpose**: Checks for urgent WhatsApp messages

### Filesystem Watcher
- **Script**: `watchers/filesystem_watcher.py`
- **Arguments**: `--vault "AI_Employee_Vault" --once`
- **Runs**: Every 30 seconds
- **Purpose**: Monitors drop folder for new files

### Daily Briefing
- **Script**: `orchestrator.py`
- **Arguments**: `--vault "AI_Employee_Vault" --briefing`
- **Runs**: 7:00 AM daily
- **Purpose**: Generates daily CEO briefing

### Weekly Audit
- **Script**: `orchestrator.py`
- **Arguments**: `--vault "AI_Employee_Vault" --weekly-audit`
- **Runs**: Sunday 10:00 PM
- **Purpose**: Generates weekly business audit

## Viewing Scheduled Tasks

### Via PowerShell

```powershell
powershell -File skills\setup_tasks.ps1 -Action list
```

### Via Task Scheduler UI

1. Open **Task Scheduler** (search in Start menu)
2. Look for tasks starting with "AI Employee -"
3. View status, triggers, and history

### Via Command Line

```cmd
schtasks /query | findstr "AI Employee"
```

## Troubleshooting

### Tasks Not Running

1. **Check Execution Policy**:
   ```powershell
   Get-ExecutionPolicy
   ```
   Should be `RemoteSigned` or `Unrestricted`

2. **Check Python Path**:
   Ensure `python` is in system PATH:
   ```cmd
   python --version
   ```

3. **Check Task History**:
   ```powershell
   Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" |
     Where-Object {$_.Message -like "*AI Employee*"} |
     Select-Object -First 10
   ```

4. **Run Manually**:
   Right-click task in Task Scheduler > **Run**

### Tasks Run But Nothing Happens

1. **Check Vault Path**: Ensure vault path is correct in task arguments
2. **Check Credentials**: Verify Gmail/WhatsApp credentials are valid
3. **Check Logs**: Review `AI_Employee_Vault/Logs/` for errors
4. **Test Manually**: Run scripts manually to see output

### Authentication Prompts

For watchers requiring authentication (Gmail, WhatsApp):
- Run them manually first to authenticate
- Sessions are saved for scheduled runs
- Re-authenticate if sessions expire

## Task Configuration Details

### Settings Applied

All tasks are configured with:
- **Allow start if on batteries**: Yes
- **Don't stop if going on batteries**: Yes
- **Start when available**: Yes
- **Multiple instances**: Ignore new (prevent duplicates)

### Working Directory

All tasks run from the project root:
```
C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0
```

### Python Executable

Tasks use:
```
python
```

Ensure this is in your system PATH.

## Modifying Schedules

### Change Task Frequency

1. Open Task Scheduler
2. Find "AI Employee - [Task Name]"
3. Right-click > **Properties**
4. Go to **Triggers** tab
5. Edit the trigger to change frequency

### Add Custom Schedule

Create a custom task in Task Scheduler:
1. **Create Basic Task**
2. Set trigger (time, event, etc.)
3. Action: Start a program
   - Program: `python`
   - Arguments: `orchestrator.py --vault "AI_Employee_Vault" --once`
   - Start in: `C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0`

## Best Practices

### Task Monitoring

- Check task status weekly
- Review logs regularly
- Monitor vault folder for new files
- Ensure watchers are authenticated

### Performance

- Don't run all watchers simultaneously if resource-constrained
- Stagger task schedules to avoid overlaps
- Monitor CPU/memory usage

### Maintenance

- Update Python/packages regularly
- Refresh authentication tokens before expiry
- Clean up old log files
- Review and adjust schedules as needed

## Uninstall All Tasks

```powershell
# Remove all tasks one by one
powershell -File skills\setup_tasks.ps1 -Task orchestrator -Action remove
powershell -File skills\setup_tasks.ps1 -Task gmail_watcher -Action remove
powershell -File skills\setup_tasks.ps1 -Task whatsapp_watcher -Action remove
powershell -File skills\setup_tasks.ps1 -Task filesystem_watcher -Action remove
powershell -File skills\setup_tasks.ps1 -Task daily_briefing -Action remove
powershell -File skills\setup_tasks.ps1 -Task weekly_audit -Action remove
```

## Next Steps

- Monitor task execution for first 24 hours
- Adjust schedules based on performance
- Set up email notifications for task failures
- Integrate with health monitoring system
