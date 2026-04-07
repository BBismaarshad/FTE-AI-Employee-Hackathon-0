# 🚀 Quick Start - Silver Tier AI Employee

Get your AI Employee up and running in 5 minutes!

## ✅ What's Already Ready

- ✅ All dependencies installed
- ✅ Gmail credentials configured
- ✅ All watchers implemented (Gmail, WhatsApp, LinkedIn, Filesystem)
- ✅ Email MCP Server ready
- ✅ LinkedIn Auto-Poster tested and working
- ✅ Complete documentation created

## 🎯 Quick Tests (No Setup Required)

Test these right now to see the system in action:

### 1. Test File Drop Workflow

```bash
# Drop a test file
echo "Review my weekly goals and suggest improvements" > drop_folder\task.txt

# Run filesystem watcher
python watchers/filesystem_watcher.py --vault .\AI_Employee_Vault --drop .\drop_folder --once

# Run orchestrator
python orchestrator.py --vault .\AI_Employee_Vault --once

# Check the plan created
dir AI_Employee_Vault\Plans /O-D
```

**Expected:** Action file in `Needs_Action/` → Plan in `Plans/`

### 2. Test LinkedIn Post Generation

```bash
# Generate a LinkedIn post draft
python skills/linkedin_poster.py --vault .\AI_Employee_Vault --generate

# View the draft
type AI_Employee_Vault\Drafts\LinkedIn\*.md
```

**Expected:** Professional LinkedIn post draft created

## 🔐 One-Time Setup (15 Minutes)

To enable full autonomous operation, complete these authentication steps:

### Step 1: Gmail Watcher (Read Emails)

```bash
python watchers/gmail_watcher.py --vault .\AI_Employee_Vault --once
```

**What happens:**
- Browser opens
- Sign in to Google
- Grant permission to read emails
- Token saved automatically

### Step 2: Email MCP Server (Send Emails)

```bash
python skills/email_mcp_server.py --credentials .\credentials\gmail_credentials.json --dry-run
```

**What happens:**
- Browser opens
- Sign in to Google
- Grant permission to send emails
- Test sending emails in dry-run mode

### Step 3: WhatsApp Watcher (Optional)

```bash
python watchers/whatsapp_watcher.py --vault .\AI_Employee_Vault --once
```

**What happens:**
- Browser opens with WhatsApp Web
- QR code appears
- Scan with your phone (WhatsApp > Linked Devices)
- Session saved

### Step 4: LinkedIn Watcher (Optional)

```bash
python watchers/linkedin_watcher.py --vault .\AI_Employee_Vault --once
```

**What happens:**
- Browser opens to LinkedIn
- Log in manually
- Session saved

### Step 5: Task Scheduler (For 24/7 Operation)

**Run PowerShell as Administrator:**

```powershell
cd C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0
powershell -ExecutionPolicy Bypass -File skills\setup_tasks.ps1 -All
```

**What happens:**
- Creates 6 scheduled tasks
- Runs automatically on schedule
- No manual intervention needed

## 📊 Verify Everything Works

### Quick Verification Commands

```bash
# Check watchers exist
python watchers/gmail_watcher.py --help
python watchers/whatsapp_watcher.py --help
python watchers/linkedin_watcher.py --help
python watchers/filesystem_watcher.py --help

# Check skills
python skills/linkedin_poster.py --help
python skills/email_mcp_server.py --help

# Check orchestrator
python orchestrator.py --help
```

### Check Vault Structure

```bash
# Verify all folders exist
dir AI_Employee_Vault
```

You should see:
- `Needs_Action/` - Pending tasks
- `Plans/` - Execution plans
- `Done/` - Completed tasks
- `Pending_Approval/` - Awaiting review
- `Approved/` - Approved actions
- `Logs/` - Audit trail
- `Drafts/LinkedIn/` - Post drafts

## 🎓 Using Your AI Employee

### Daily Workflow (After Setup)

**Morning:**
1. Check dashboard: Open `AI_Employee_Vault/Dashboard.md`
2. Review pending actions: Check `Needs_Action/`
3. Approve pending items: Move files from `Pending_Approval/` to `Approved/`

**Throughout Day:**
- Drop files in `drop_folder/` for AI processing
- Send emails (AI will detect replies)
- Get WhatsApp messages monitored automatically

**Evening:**
- Check completed tasks in `Done/`
- Review logs in `Logs/`
- Approve any pending LinkedIn posts

### On-Demand Commands

```bash
# Process all pending tasks
python orchestrator.py --vault .\AI_Employee_Vault --once

# Check for new emails
python watchers/gmail_watcher.py --vault .\AI_Employee_Vault --once

# Generate LinkedIn post
python skills/linkedin_poster.py --vault .\AI_Employee_Vault --generate

# Process dropped files
python watchers/filesystem_watcher.py --vault .\AI_Employee_Vault --drop .\drop_folder --once
```

## 📚 Documentation

### Complete Guides

- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Detailed setup instructions
- **[SILVER_COMPLETION_SUMMARY.md](./SILVER_COMPLETION_SUMMARY.md)** - What was built
- **[SILVER_TIER_README.md](./SILVER_TIER_README.md)** - Architecture & usage

### Skill Documentation

- **[Gmail Watcher](.qwen/skills/gmail-watcher/SKILL.md)** - Email monitoring
- **[WhatsApp Watcher](.qwen/skills/whatsapp-watcher/SKILL.md)** - Message monitoring
- **[LinkedIn Watcher](.qwen/skills/linkedin-watcher/SKILL.md)** - Network monitoring
- **[LinkedIn Auto-Poster](.qwen/skills/linkedin-auto-poster/SKILL.md)** - Content generation
- **[Email MCP Server](.qwen/skills/email-mcp-server/SKILL.md)** - Email sending
- **[Windows Task Scheduler](.qwen/skills/windows-task-scheduler/SKILL.md)** - Automation

## 🐛 Troubleshooting

### Common Issues

**Problem:** "Module not found"
**Solution:** Make sure you're in the project root directory

**Problem:** "Credentials not found"
**Solution:** Check `credentials/gmail_credentials.json` exists

**Problem:** "Unicode encoding error"
**Solution:** Already fixed in current version

**Problem:** "Task scheduler won't create"
**Solution:** Run PowerShell as Administrator

### Get Help

1. Check the skill-specific SKILL.md files
2. Review logs in `AI_Employee_Vault/Logs/`
3. Run commands manually to see full error output
4. Check SETUP_GUIDE.md for detailed troubleshooting

## 🎯 Next Steps

### After Basic Setup

1. **Monitor for 24 hours** - Ensure watchers are running
2. **Test email workflow** - Send yourself an email and see if detected
3. **Generate LinkedIn posts** - Test different categories
4. **Review approval workflow** - Test the complete flow

### Upgrade to Gold Tier

When ready for more features:
- Odoo accounting integration
- Facebook/Instagram/Twitter posting
- CEO briefing generation
- Ralph Wiggum autonomous loop
- Error recovery systems

## 🏆 Success Criteria Met

✅ Multiple watchers (Gmail + WhatsApp + LinkedIn + Filesystem)  
✅ LinkedIn auto-posting with approval workflow  
✅ Email MCP server for sending messages  
✅ Plan generation from action files  
✅ Human-in-the-loop approval system  
✅ Task scheduling via Windows Task Scheduler  
✅ Complete Agent Skills documentation  

**Silver Tier Status: COMPLETE ✅**

---

**Need Help?**
- Read: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- Review: [SILVER_COMPLETION_SUMMARY.md](./SILVER_COMPLETION_SUMMARY.md)
- Join: Wednesday Research Meetings on Zoom

**Built with Qwen Code - The Brain of Your AI Employee**
