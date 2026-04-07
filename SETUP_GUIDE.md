# Silver Tier Setup Guide

Complete step-by-step guide for setting up and running the Silver Tier AI Employee.

## ✅ What's Already Done

- ✅ All dependencies installed
- ✅ Gmail credentials configured in `credentials/gmail_credentials.json`
- ✅ Playwright browser installed
- ✅ All watcher scripts implemented (Gmail, WhatsApp, LinkedIn, Filesystem)
- ✅ Email MCP Server ready
- ✅ LinkedIn Auto-Poster ready
- ✅ Agent Skills documentation created
- ✅ Windows Task Scheduler script ready

## 🚀 Setup Instructions

### Step 1: Authenticate Gmail Watcher

The Gmail Watcher needs to authenticate with your Google account once.

```bash
python watchers/gmail_watcher.py --vault .\AI_Employee_Vault --credentials .\credentials\gmail_credentials.json --once
```

**What will happen:**
1. A browser window will open
2. You'll be asked to sign in to your Google account
3. You'll need to grant permission to read your emails
4. A token file will be saved in `credentials/token.json`
5. The watcher will check for unread emails and exit

**After successful authentication:**
- The token is saved automatically
- You won't need to authenticate again unless the token expires
- Check your `AI_Employee_Vault/Needs_Action/` folder for any email action files

### Step 2: Authenticate Email MCP Server

The Email MCP Server needs permission to **send** emails (separate from reading).

```bash
python skills/email_mcp_server.py --credentials .\credentials\gmail_credentials.json --dry-run
```

**What will happen:**
1. A browser window will open
2. Sign in and grant permission to send emails
3. Token saved for future use
4. You can test sending emails in dry-run mode

### Step 3: Authenticate WhatsApp Watcher (Optional)

The WhatsApp Watcher requires QR code scanning.

```bash
python watchers/whatsapp_watcher.py --vault .\AI_Employee_Vault --once
```

**What will happen:**
1. A browser window opens with WhatsApp Web
2. A QR code will be displayed
3. Open WhatsApp on your phone
4. Go to Settings/Menu > Linked Devices
5. Tap "Link a Device" and scan the QR code
6. Session saved in `credentials/whatsapp_session/`

**Note:** If you don't need WhatsApp monitoring, you can skip this step.

### Step 4: Test LinkedIn Watcher (Optional)

The LinkedIn Watcher requires manual login.

```bash
python watchers/linkedin_watcher.py --vault .\AI_Employee_Vault --once
```

**What will happen:**
1. A browser window opens to LinkedIn
2. You need to log in with your LinkedIn credentials
3. Session saved in `credentials/linkedin_session/`

**Warning:** Automated LinkedIn access may violate LinkedIn's Terms of Service. Use at your own risk.

### Step 5: Test LinkedIn Auto-Poster

Generate a sample LinkedIn post draft:

```bash
python skills/linkedin_poster.py --vault .\AI_Employee_Vault --generate
```

**Expected output:**
```
✅ Draft created: AI_Employee_Vault\Drafts\LinkedIn\2026-04-06_service_announcement.md
```

Check the draft in: `AI_Employee_Vault/Drafts/LinkedIn/`

### Step 6: Test Filesystem Watcher

Create a test file in the drop folder:

```bash
echo "Test task for AI Employee" > drop_folder\test_task.txt
```

Run the filesystem watcher:

```bash
python watchers/filesystem_watcher.py --vault .\AI_Employee_Vault --drop .\drop_folder --once
```

Check for action file in: `AI_Employee_Vault/Needs_Action/`

### Step 7: Test Orchestrator

Run the orchestrator to process any pending action files:

```bash
python orchestrator.py --vault .\AI_Employee_Vault --once
```

Check for plans in: `AI_Employee_Vault/Plans/`

### Step 8: Set Up Windows Task Scheduler (Recommended)

For 24/7 autonomous operation, set up scheduled tasks.

**Important:** Run PowerShell as Administrator first!

```powershell
# Navigate to project directory
cd C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0

# Set up all scheduled tasks
powershell -ExecutionPolicy Bypass -File skills\setup_tasks.ps1 -All
```

**Tasks that will be created:**
- Orchestrator: Every 5 minutes
- Gmail Watcher: Every 2 minutes
- WhatsApp Watcher: Every 1 minute
- Filesystem Watcher: Every 30 seconds
- Daily Briefing: 7:00 AM
- Weekly Audit: Sunday 10:00 PM

**Verify tasks:**

```powershell
powershell -File skills\setup_tasks.ps1 -Action list
```

## 🧪 Testing Workflow

### Test Email Workflow

1. **Send yourself an email** or mark an email as unread
2. **Run Gmail Watcher:**
   ```bash
   python watchers/gmail_watcher.py --vault .\AI_Employee_Vault --once
   ```
3. **Check for action file:** `AI_Employee_Vault/Needs_Action/EMAIL_*.md`
4. **Run Orchestrator:**
   ```bash
   python orchestrator.py --vault .\AI_Employee_Vault --once
   ```
5. **Check for plan:** `AI_Employee_Vault/Plans/PLAN_*.md`

### Test LinkedIn Post Generation

1. **Generate draft:**
   ```bash
   python skills/linkedin_poster.py --vault .\AI_Employee_Vault --generate
   ```
2. **Review draft:** `AI_Employee_Vault/Drafts/LinkedIn/*.md`
3. **Edit if needed**
4. **Create approval:**
   ```bash
   python skills/linkedin_poster.py --vault .\AI_Employee_Vault --post
   ```
5. **Approve:** Move approval file to `Approved/LinkedIn/`

### Test File Drop Workflow

1. **Drop a file:** `drop_folder/my_task.txt`
2. **Run Filesystem Watcher:**
   ```bash
   python watchers/filesystem_watcher.py --vault .\AI_Employee_Vault --drop .\drop_folder --once
   ```
3. **Check action file:** `AI_Employee_Vault/Needs_Action/FILE_*.md`
4. **Run Orchestrator:**
   ```bash
   python orchestrator.py --vault .\AI_Employee_Vault --once
   ```

## 📋 Verification Checklist

Use this checklist to verify everything is working:

- [ ] Gmail Watcher authenticates successfully
- [ ] Gmail token saved in `credentials/token.json`
- [ ] Unread emails create action files in `Needs_Action/`
- [ ] Email MCP Server authenticates
- [ ] Email MCP can send emails (test with `--dry-run`)
- [ ] LinkedIn Auto-Poster generates drafts
- [ ] Drafts appear in `Drafts/LinkedIn/`
- [ ] Filesystem Watcher detects new files
- [ ] Orchestrator processes action files
- [ ] Plans created in `Plans/`
- [ ] Windows Task Scheduler tasks created
- [ ] Tasks run on schedule

## 🔧 Troubleshooting

### Gmail Authentication Fails

**Problem:** "Gmail credentials file not found"
**Solution:** Ensure `credentials/gmail_credentials.json` exists

**Problem:** "Token expired"
**Solution:** Delete `credentials/token.json` and re-authenticate

**Problem:** Browser doesn't open
**Solution:** Run without `--once` to see full output

### WhatsApp QR Code Issues

**Problem:** QR code doesn't appear
**Solution:** Run without `--headless` flag to see browser

**Problem:** Session expires quickly
**Solution:** Normal - WhatsApp sessions expire after ~30-90 days

### LinkedIn Login Issues

**Problem:** Can't find login button
**Solution:** LinkedIn may have changed their UI - update watcher

**Problem:** Session not persisting
**Solution:** Check `credentials/linkedin_session/` folder exists

### Tasks Not Running

**Problem:** Scheduled tasks don't execute
**Solution:** 
1. Ensure running as Administrator when creating tasks
2. Check Python is in system PATH: `python --version`
3. Verify task paths in Task Scheduler

**Problem:** Tasks run but nothing happens
**Solution:**
1. Check vault path in task arguments
2. Review logs in `AI_Employee_Vault/Logs/`
3. Run scripts manually to see errors

### Unicode/Encoding Errors

**Problem:** "charmap codec can't encode character"
**Solution:** This has been fixed in the current version with UTF-8 encoding

## 📊 Monitoring Your AI Employee

### Check Recent Activity

```bash
# View latest action files
dir AI_Employee_Vault\Needs_Action /O-D

# View latest plans
dir AI_Employee_Vault\Plans /O-D

# View today's logs
type AI_Employee_Vault\Logs\2026-04-06.json
```

### Monitor Dashboard

Open `AI_Employee_Vault/Dashboard.md` in Obsidian or any text editor to see:
- Recent activity
- Pending tasks
- System status

### Review Logs

```bash
# View email operations
type AI_Employee_Vault\Logs\email_operations.json

# View LinkedIn posts
type AI_Employee_Vault\Logs\linkedin_posts.json
```

## 🎯 Next Steps (Gold Tier)

After mastering Silver tier, you can upgrade to Gold tier:

1. **Odoo Accounting Integration** - Self-hosted ERP system
2. **Social Media Expansion** - Facebook, Instagram, Twitter/X
3. **CEO Briefing Generation** - Automated weekly reports
4. **Ralph Wiggum Loop** - Autonomous multi-step task completion
5. **Error Recovery** - Graceful degradation and retry logic

## 📚 Resources

- [Gmail Watcher Skill](.qwen/skills/gmail-watcher/SKILL.md)
- [LinkedIn Watcher Skill](.qwen/skills/linkedin-watcher/SKILL.md)
- [WhatsApp Watcher Skill](.qwen/skills/whatsapp-watcher/SKILL.md)
- [LinkedIn Auto-Poster Skill](.qwen/skills/linkedin-auto-poster/SKILL.md)
- [Email MCP Server Skill](.qwen/skills/email-mcp-server/SKILL.md)
- [Windows Task Scheduler Skill](.qwen/skills/windows-task-scheduler/SKILL.md)

## 🆘 Getting Help

- Check the main README.md for architecture overview
- Review QWEN.md for Qwen Code integration details
- Join Wednesday Research Meetings on Zoom
- Watch tutorials on Panaversity YouTube channel

---

**Silver Tier Status: ✅ COMPLETE**

All core components implemented and tested. Ready for autonomous operation!
