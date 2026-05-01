# 🚀 Quick Start - Gold Tier AI Employee

Get your autonomous AI Employee up and running with full business integration!

## ✅ What's Already Ready

### Silver Tier (Complete)
- ✅ All dependencies installed
- ✅ Gmail credentials configured
- ✅ All watchers implemented (Gmail, WhatsApp, LinkedIn, Filesystem)
- ✅ Email MCP Server ready
- ✅ LinkedIn Auto-Poster tested and working
- ✅ Complete documentation created

### Gold Tier (Complete)
- ✅ Facebook & Instagram Poster
- ✅ Odoo MCP Server (Accounting Integration)
- ✅ Weekly Business Audit (CEO Briefing)
- ✅ Ralph Wiggum Loop (Autonomous Completion)
- ✅ Docker Compose for Odoo 19
- ✅ Complete Gold Tier documentation

## 🎯 Quick Tests (No Setup Required)

### Silver Tier Tests

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

### Gold Tier Tests

#### Test Facebook Post Generation

```bash
# Generate a Facebook post draft
python skills/facebook_poster.py --vault .\AI_Employee_Vault --generate --category business_update

# View the draft
type AI_Employee_Vault\Drafts\Facebook\*.md
```

**Expected:** Facebook post draft with professional content

#### Test Odoo MCP (Dry Run)

```bash
# Test Odoo integration without connecting
python skills/odoo_mcp.py --dry-run

# Interactive mode
odoo> partners
odoo> summary
odoo> exit
```

**Expected:** Simulated Odoo operations

#### Test Weekly Audit

```bash
# Generate CEO briefing
python skills/weekly_audit.py --vault .\AI_Employee_Vault

# View the briefing
type AI_Employee_Vault\Briefings\*_Monday_CEO_Briefing.md
```

**Expected:** Comprehensive business briefing generated

#### Test Ralph Loop (Dry Run)

```bash
# Test autonomous completion loop
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Test task" --promise "DONE" --max-iterations 2
```

**Expected:** Loop executes with iteration tracking

## 🔐 One-Time Setup

### Silver Tier Setup (15 Minutes)

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

### Gold Tier Setup (30 Minutes)

#### Step 6: Setup Odoo (Accounting System)

**Start Odoo with Docker:**

```bash
# Navigate to Odoo directory
cd docker\odoo

# Copy environment file
copy .env.example .env

# Start Odoo
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f odoo
```

**Access Odoo:**
1. Open browser: http://localhost:8069
2. Create database: `odoo`
3. Set admin password
4. Install Accounting module

**Test Connection:**

```bash
# Test Odoo MCP connection
python skills\odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password your_password

# Try commands
odoo> partners
odoo> summary
odoo> exit
```

#### Step 7: Setup Facebook Poster

```bash
# Generate first post
python skills\facebook_poster.py --vault .\AI_Employee_Vault --generate --category business_update

# Review draft in Drafts/Facebook/

# Test posting (dry run)
python skills\facebook_poster.py --vault .\AI_Employee_Vault --process-approved --dry-run
```

**First-time login:**
- Browser opens to Facebook
- Log in manually
- Session saved for future use

#### Step 8: Schedule Gold Tier Tasks

**Run PowerShell as Administrator:**

```powershell
# Weekly CEO Briefing (Sunday 8 PM)
schtasks /create /tn "AI_Employee_Weekly_Audit" /tr "python C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\skills\weekly_audit.py --vault C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\AI_Employee_Vault --odoo-url http://localhost:8069 --odoo-db odoo --odoo-user admin" /sc weekly /d SUN /st 20:00

# Daily Facebook Post Draft (8 AM)
schtasks /create /tn "AI_Employee_Facebook_Draft" /tr "python C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\skills\facebook_poster.py --vault C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\AI_Employee_Vault --generate" /sc daily /st 08:00

# Process Approved Posts (9 AM, 1 PM, 7 PM)
schtasks /create /tn "AI_Employee_Facebook_Post_Morning" /tr "python C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\skills\facebook_poster.py --vault C:\Users\bisma\Desktop\FTE-AI-Employee-Hackathon-0\AI_Employee_Vault --process-approved" /sc daily /st 09:00
```

## 📊 Verify Everything Works

### Silver Tier Verification

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

### Gold Tier Verification

```bash
# Check Gold Tier skills
python skills/facebook_poster.py --help
python skills/odoo_mcp.py --help
python skills/weekly_audit.py --help
python skills/ralph_loop.py --help

# Check Odoo is running
docker compose -f docker\odoo\docker-compose.yml ps

# Test Odoo connection
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password admin --dry-run
```
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
- `Drafts/LinkedIn/` - LinkedIn post drafts
- `Drafts/Facebook/` - Facebook post drafts (Gold)
- `Briefings/` - CEO briefings (Gold)

## 🎓 Using Your AI Employee

### Silver Tier Daily Workflow

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

### Gold Tier Weekly Workflow

**Monday Morning:**
1. Read CEO Briefing in `Briefings/`
2. Review financial metrics from Odoo
3. Address identified bottlenecks
4. Implement proactive suggestions

**Daily:**
- Review Facebook post drafts
- Approve posts for publishing
- Monitor Odoo invoices and payments
- Check accounting summaries

**Sunday Evening:**
- Weekly audit runs automatically
- CEO briefing generated
- Review ready for Monday morning

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

# Generate Facebook post (Gold)
python skills/facebook_poster.py --vault .\AI_Employee_Vault --generate --category tip

# Generate CEO briefing (Gold)
python skills/weekly_audit.py --vault .\AI_Employee_Vault

# Run autonomous task loop (Gold)
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Process all pending emails" --promise "DONE" --max-iterations 5

# Check Odoo accounts (Gold)
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password admin
```

## 📚 Documentation

### Complete Guides

- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Detailed setup instructions
- **[SILVER_COMPLETION_SUMMARY.md](./SILVER_COMPLETION_SUMMARY.md)** - Silver Tier completion
- **[GOLD_COMPLETION_SUMMARY.md](./GOLD_COMPLETION_SUMMARY.md)** - Gold Tier completion
- **[SILVER_TIER_README.md](./SILVER_TIER_README.md)** - Silver architecture & usage

### Skill Documentation

**Silver Tier:**
- **[Gmail Watcher](.qwen/skills/gmail-watcher/SKILL.md)** - Email monitoring
- **[WhatsApp Watcher](.qwen/skills/whatsapp-watcher/SKILL.md)** - Message monitoring
- **[LinkedIn Watcher](.qwen/skills/linkedin-watcher/SKILL.md)** - Network monitoring
- **[LinkedIn Auto-Poster](.qwen/skills/linkedin-auto-poster/SKILL.md)** - Content generation
- **[Email MCP Server](.qwen/skills/email-mcp-server/SKILL.md)** - Email sending
- **[Windows Task Scheduler](.qwen/skills/windows-task-scheduler/SKILL.md)** - Automation

**Gold Tier:**
- **[Facebook Poster](.qwen/skills/facebook-poster/SKILL.md)** - Facebook & Instagram automation
- **[Odoo MCP Server](.qwen/skills/odoo-mcp/SKILL.md)** - Accounting integration
- **[Weekly Audit](.qwen/skills/weekly-audit/SKILL.md)** - CEO briefing generation
- **[Ralph Loop](.qwen/skills/ralph-loop/SKILL.md)** - Autonomous task completion

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


## 🏆 Success Criteria Met

### Silver Tier ✅
✅ Multiple watchers (Gmail + WhatsApp + LinkedIn + Filesystem)  
✅ LinkedIn auto-posting with approval workflow  
✅ Email MCP server for sending messages  
✅ Plan generation from action files  
✅ Human-in-the-loop approval system  
✅ Task scheduling via Windows Task Scheduler  
✅ Complete Agent Skills documentation

### Gold Tier ✅
✅ Facebook & Instagram integration  
✅ Odoo Community Edition (self-hosted accounting)  
✅ Weekly Business Audit with CEO Briefing  
✅ Ralph Wiggum Loop (autonomous completion)  
✅ Docker Compose for Odoo 19  
✅ Complete Gold Tier documentation  
✅ Cross-domain integration (Personal + Business)  
✅ Error recovery and graceful degradation  
✅ Comprehensive audit logging  

---

**Need Help?**
- Read: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- Review: [SILVER_COMPLETION_SUMMARY.md](./SILVER_COMPLETION_SUMMARY.md)
- Join: Wednesday Research Meetings on Zoom

**🥇 Gold Tier Complete - Autonomous Business Employee Ready**

Built with Claude Code - The Brain of Your AI Employee
