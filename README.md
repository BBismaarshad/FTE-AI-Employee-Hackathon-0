# Digital FTE - AI Employee (Bronze Tier)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A minimum viable **Personal AI Employee** built for the FTE-AI-Employee Hackathon. This Bronze Tier implementation provides the foundation for an autonomous AI agent that proactively manages your personal and business affairs using Claude Code and Obsidian.

## 🏆 Bronze Tier Deliverables

- ✅ **Obsidian vault** with Dashboard.md, Company_Handbook.md, and Business_Goals.md
- ✅ **One working Watcher script** (Filesystem monitoring)
- ✅ **Claude Code integration** - reads from and writes to the vault
- ✅ **Basic folder structure**: /Inbox, /Needs_Action, /Done, /Plans, /Pending_Approval, /Approved, /Rejected, /Logs
- ✅ **Agent Skills ready** - all AI functionality designed as extensible skills

## 📁 Project Structure

```
FTE-AI-Employee-Hackathon-0/
├── AI_Employee_Vault/          # Obsidian vault (local knowledge base)
│   ├── Dashboard.md            # Real-time status summary
│   ├── Company_Handbook.md     # Rules of engagement for AI
│   ├── Business_Goals.md       # Objectives and targets
│   ├── Inbox/                  # Raw incoming files
│   ├── Needs_Action/           # Items requiring AI attention
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # AI-generated action plans
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Human-approved actions
│   ├── Rejected/               # Rejected actions
│   ├── Logs/                   # Daily JSON activity logs
│   ├── Briefings/              # CEO briefings (future tiers)
│   └── Accounting/             # Financial records (future tiers)
│
├── watchers/                   # Watcher scripts (AI's "senses")
│   ├── base_watcher.py         # Abstract base class for all watchers
│   └── filesystem_watcher.py   # Monitors drop folder for files
│
├── drop_folder/                # Drop files here for AI processing
├── orchestrator.py             # Master process managing the system
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules (security-first)
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

| Component | Required | Purpose |
|-----------|----------|---------|
| Python 3.13+ | ✅ | Watcher scripts & orchestrator |
| Qwen Code | ✅ | AI reasoning engine |
| Obsidian (optional) | Recommended | View/edit vault files |
| Node.js 24+ | For future tiers | MCP servers |

### Setup (5 minutes)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FTE-AI-Employee-Hackathon-0
   ```

2. **Copy environment template**
   ```bash
   copy .env.example .env
   # Edit .env and add any API keys (not needed for Bronze tier)
   ```

3. **Verify Qwen Code is installed**
   ```bash
   qwen --version
   ```

4. **Open the vault in Obsidian** (optional but recommended)
   - Open Obsidian → Open folder as vault → Select `AI_Employee_Vault/`

## 📖 Usage

### Method 1: File Drop Workflow (Easiest)

1. **Drop a file** into the `drop_folder/` directory
   ```bash
   # Example: Copy a text file or document
   copy my_task.txt drop_folder\
   ```

2. **Run the filesystem watcher** (creates action file in vault)
   ```bash
   python watchers\filesystem_watcher.py --vault AI_Employee_Vault --drop drop_folder --once
   ```

3. **Run the orchestrator** (processes the action file, creates a plan)
   ```bash
   python orchestrator.py --vault AI_Employee_Vault --once
   ```

4. **Review the plan** in `AI_Employee_Vault/Plans/`

5. **Use Qwen Code** to process the plan:
   ```bash
   qwen --cwd AI_Employee_Vault
   # Prompt: "Check the Plans folder and process any pending plans"
   ```

### Method 2: Direct Vault Editing

1. **Create a task file** directly in `AI_Employee_Vault/Needs_Action/`:
   ```markdown
   ---
   type: task
   priority: high
   created: 2026-04-05T10:00:00Z
   status: pending
   ---

   # Task: Review weekly goals

   Please review the Business_Goals.md file and suggest improvements.
   ```

2. **Run the orchestrator**:
   ```bash
   python orchestrator.py --vault AI_Employee_Vault --once
   ```

3. **Check the Plans folder** for the generated plan.

### Method 3: Continuous Monitoring

Run the watchers and orchestrator continuously in the background:

```bash
# Terminal 1: Filesystem watcher
python watchers\filesystem_watcher.py --vault AI_Employee_Vault --drop drop_folder

# Terminal 2: Orchestrator
python orchestrator.py --vault AI_Employee_Vault
```

Now just drop files into `drop_folder/` and the system will automatically process them.

## 🤖 Qwen Code Integration

Qwen Code is the "brain" of the AI Employee. Point it at the vault:

```bash
cd AI_Employee_Vault
qwen
```

### Useful Qwen Code Prompts

- *"Check the Needs_Action folder and process all pending tasks"*
- *"Review the Plans folder and execute the first pending plan"*
- *"Read Company_Handbook.md and summarize the key rules"*
- *"Update Dashboard.md with today's activity"*
- *"Generate a weekly summary of all files in the Done folder"*

### Ralph Wiggum Loop (Autonomous Task Completion)

Keep Qwen working until a task is complete:

```bash
/ralph-loop "Process all files in Needs_Action, move to Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## 📋 Vault Templates

### Dashboard.md
Real-time summary of system status, pending tasks, and recent activity.

### Company_Handbook.md
Defines how the AI should behave - communication rules, financial rules, safety rules, and ethics.

### Business_Goals.md
Tracks revenue targets, active projects, and key metrics. Update weekly.

## 🔒 Security

- **No credentials stored in vault** - all secrets go in `.env`
- **`.env` is gitignored** - never committed to version control
- **Human-in-the-loop** - sensitive actions require approval file movement
- **Audit logging** - all actions logged to `Logs/YYYY-MM-DD.json`
- **Dry-run mode** - set `DRY_RUN=true` in `.env` for testing

## 🧪 Testing

Test the filesystem watcher:

```bash
# Create a test file
echo "Test task for AI Employee" > drop_folder\test_task.txt

# Run watcher once
python watchers\filesystem_watcher.py --vault AI_Employee_Vault --drop drop_folder --once

# Check Needs_Action folder for created action file
dir AI_Employee_Vault\Needs_Action

# Run orchestrator
python orchestrator.py --vault AI_Employee_Vault --once

# Check Plans folder
dir AI_Employee_Vault\Plans
```

## 🛣️ Roadmap to Higher Tiers

### Silver Tier (Next Steps)
- [ ] Add Gmail Watcher (requires Google API credentials)
- [ ] Add WhatsApp Watcher (requires Playwright)
- [ ] MCP server for sending emails
- [ ] Human-in-the-loop approval workflow
- [ ] Scheduled tasks via cron/Task Scheduler

### Gold Tier
- [ ] Full cross-domain integration
- [ ] Odoo accounting integration
- [ ] Social media posting
- [ ] Weekly CEO Briefing generation
- [ ] Ralph Wiggum loop for autonomous completion

### Platinum Tier
- [ ] Always-on cloud deployment
- [ ] Cloud/Local work-zone specialization
- [ ] Vault sync with claim-by-move rules

## 🐛 Troubleshooting

### "Command not found: qwen"
Install Qwen Code first, then verify installation:
```bash
qwen --version
```

### No action files created
- Check that `drop_folder/` exists and has files
- Verify the watcher is pointed at the correct paths
- Check console output for errors

### Orchestrator not processing files
- Ensure `AI_Employee_Vault/Needs_Action/` has `.md` files
- Check file permissions allow read/write access
- Review logs in `AI_Employee_Vault/Logs/`

## 📚 Resources

- [Qwen Code Documentation](https://qwenlm.github.io/)
- [Obsidian Download](https://obsidian.md/download)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

## 👥 Community

- **Research Meetings**: Every Wednesday at 10:00 pm on Zoom
- **YouTube**: https://www.youtube.com/@panaversity

## 📄 License

Built for the FTE-AI-Employee Hackathon 2026.

---
*AI Employee v0.1.0 - Bronze Tier*
*Local-first, agent-driven, human-in-the-loop*
