# Weekly Business Audit - Agent Skill

**Tier:** Gold  
**Category:** Business Intelligence & Reporting  
**Status:** ✅ Ready

## Overview

Generates comprehensive Monday Morning CEO Briefings with business performance analysis, accounting audits, bottleneck identification, and proactive suggestions. Transforms raw data into actionable insights.

## Features

- 📊 **Performance Analysis** - Compare actual vs goals
- 💰 **Financial Tracking** - Revenue, expenses, balances
- 🔍 **Bottleneck Detection** - Identify workflow issues
- 💡 **Proactive Suggestions** - AI-driven recommendations
- 📈 **Trend Analysis** - Week-over-week comparisons
- 🔗 **Odoo Integration** - Real-time accounting data
- 📝 **Markdown Reports** - Beautiful, readable briefings

## Installation

### Prerequisites

```bash
# All dependencies already installed
# Optional: Odoo for accounting data
```

### Verify Installation

```bash
python skills/weekly_audit.py --help
```

## Usage

### Basic Audit (Log-Based)

```bash
python skills/weekly_audit.py --vault .\AI_Employee_Vault
```

This generates a briefing using:
- Completed tasks from Done/ folder
- Action logs from Logs/ folder
- Business goals from Business_Goals.md

### Audit with Odoo Integration

```bash
python skills/weekly_audit.py --vault .\AI_Employee_Vault --odoo-url http://localhost:8069 --odoo-db odoo --odoo-user admin --odoo-password admin
```

This adds real-time accounting data:
- Revenue from posted invoices
- Accounts receivable/payable
- Pending invoices
- Financial metrics

### Scheduled Weekly Audit

```powershell
# Run every Sunday at 8 PM
schtasks /create /tn "AI_Employee_Weekly_Audit" /tr "python skills\weekly_audit.py --vault .\AI_Employee_Vault --odoo-url http://localhost:8069 --odoo-db odoo --odoo-user admin" /sc weekly /d SUN /st 20:00
```

## Output

### CEO Briefing Structure

```markdown
# Monday Morning CEO Briefing

## Executive Summary
Business performance is **Strong** this week. 15 tasks completed with 42 automated actions.

## Financial Performance
| Metric | Amount |
|--------|--------|
| Revenue | $2,450.00 |
| Expenses | $450.00 |
| Net Balance | $2,000.00 |

## Completed Activities
- Task completions
- Automated actions
- Recent highlights

## Bottlenecks & Issues
- Stale tasks
- Incomplete plans
- Workflow issues

## Proactive Suggestions
- Revenue optimization
- Process improvements
- Action items

## Next Week Focus
- Priorities
- Follow-ups
- Goals
```

### Example Output

```
📊 WEEKLY BUSINESS AUDIT
═══════════════════════════════════════════════════════════

✅ CEO Briefing generated: AI_Employee_Vault/Briefings/2026-05-01_Monday_CEO_Briefing.md

═══════════════════════════════════════════════════════════

📖 Open the briefing in Obsidian to review this week's performance.
```

## Data Sources

### 1. Business Goals

Reads from `Business_Goals.md`:
- Revenue targets
- Key metrics
- Active projects
- Success criteria

### 2. Activity Logs

Analyzes `Logs/*.json`:
- Completed tasks
- Automated actions
- Email activity
- Social media posts

### 3. Task Completion

Scans `Done/` folder:
- Completed tasks (last 7 days)
- Task categories
- Completion dates

### 4. Accounting Data

From Odoo (if configured):
- Posted invoices
- Pending invoices
- Receivables/payables
- Account balances

## Metrics Tracked

### Financial Metrics

- **Revenue** - Total from invoices/logs
- **Expenses** - Outbound payments
- **Net Balance** - Revenue minus expenses
- **Receivable** - Outstanding customer invoices
- **Payable** - Outstanding supplier bills

### Activity Metrics

- **Completed Tasks** - Tasks moved to Done/
- **Automated Actions** - Actions logged
- **Email Volume** - Emails sent/received
- **Social Posts** - Posts published

### Performance Indicators

- **Trend** - Strong / Moderate / Needs attention
- **Bottlenecks** - Workflow issues identified
- **Suggestions** - AI-generated recommendations

## Bottleneck Detection

### Stale Tasks

```
🟡 3 tasks in Needs_Action older than 3 days
```

**Triggers:**
- Tasks in Needs_Action > 3 days old

**Severity:** Medium

### Incomplete Plans

```
🔴 8 plans with incomplete tasks
```

**Triggers:**
- More than 5 plans with unchecked items

**Severity:** High

## Proactive Suggestions

### Revenue-Based

- No revenue → Review sales pipeline
- High revenue → Scale successful strategies
- Pending invoices → Prepare for review

### Activity-Based

- Low task completion → Review priorities
- High productivity → Maintain momentum
- No social posts → Schedule content

### Email-Based

- High volume → Consider templates
- Low engagement → Review messaging

## Configuration

### Business Goals Template

Create `Business_Goals.md`:

```markdown
# Business Goals

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Response time | < 24h | > 48h |
| Payment rate | > 90% | < 80% |

### Active Projects
1. Project Alpha - Due Jan 15 - Budget $2,000
2. Project Beta - Due Jan 30 - Budget $3,500
```

### Environment Variables

```bash
# Set Odoo password
export ODOO_PASSWORD=your_password

# Run audit
python skills/weekly_audit.py --vault .\AI_Employee_Vault --odoo-url http://localhost:8069 --odoo-db odoo --odoo-user admin
```

## Integration

### With Orchestrator

```python
from skills.weekly_audit import WeeklyAudit

audit = WeeklyAudit(vault_path='./AI_Employee_Vault')
briefing_path = audit.run_audit()
print(f"Briefing: {briefing_path}")
```

### With Odoo MCP

```python
from skills.odoo_mcp import OdooMCP
from skills.weekly_audit import WeeklyAudit

# Initialize Odoo
odoo = OdooMCP(url='http://localhost:8069', db='odoo', username='admin', password='admin')

# Run audit with Odoo data
audit = WeeklyAudit(vault_path='./AI_Employee_Vault', odoo_client=odoo)
briefing_path = audit.run_audit()
```

### With Email Notifications

```python
from skills.weekly_audit import WeeklyAudit
from skills.email_mcp_server import EmailMCP

# Generate briefing
audit = WeeklyAudit(vault_path='./AI_Employee_Vault')
briefing_path = audit.run_audit()

# Read briefing
briefing_content = briefing_path.read_text()

# Send via email
email = EmailMCP(credentials_path='./credentials/gmail_credentials.json')
email.send_email(
    to='ceo@company.com',
    subject='Monday Morning CEO Briefing',
    body=briefing_content
)
```

## Customization

### Custom Metrics

Add custom metrics in `_analyze_performance()`:

```python
def _analyze_performance(self, goals, activity, accounting, bottlenecks, suggestions):
    # Add custom metric
    custom_metric = self._calculate_custom_metric(activity)
    
    return {
        # ... existing metrics
        'custom_metric': custom_metric
    }
```

### Custom Suggestions

Add suggestion logic in `_generate_suggestions()`:

```python
def _generate_suggestions(self, goals, activity, accounting):
    suggestions = []
    
    # Custom suggestion logic
    if custom_condition:
        suggestions.append("💡 Custom suggestion here")
    
    return suggestions
```

### Custom Briefing Format

Modify `_generate_briefing()` to change output format:

```python
def _generate_briefing(self, summary):
    # Custom markdown format
    content = f"""
    # Custom Briefing Format
    
    Your custom sections here...
    """
    return filepath
```

## Troubleshooting

### Issue: "No Business_Goals.md found"

**Solution:**
1. Create `Business_Goals.md` in vault root
2. Use template from Configuration section
3. Audit will use default message if missing

### Issue: "No activity data"

**Cause:** Empty Logs/ or Done/ folders

**Solution:**
1. Run watchers to generate logs
2. Complete some tasks
3. Wait for data accumulation

### Issue: "Odoo connection failed"

**Solution:**
1. Verify Odoo is running
2. Check credentials
3. Audit falls back to log-based data

### Issue: "Unicode encoding error"

**Solution:** Already fixed - all files use UTF-8

## Best Practices

### Weekly Schedule

- **Sunday 8 PM** - Generate briefing
- **Monday 8 AM** - Review briefing
- **Monday 9 AM** - Act on suggestions

### Review Process

1. Read Executive Summary
2. Check Financial Performance
3. Review Bottlenecks
4. Implement Suggestions
5. Update Business Goals

### Data Quality

- Keep Business_Goals.md updated
- Ensure watchers are running
- Complete tasks properly
- Log all actions

## Advanced Usage

### Multi-Period Analysis

```python
# Generate briefings for multiple weeks
for week in range(4):
    audit = WeeklyAudit(vault_path='./AI_Employee_Vault')
    briefing = audit.run_audit()
    # Compare trends across weeks
```

### Custom Reporting

```python
# Generate custom report
audit = WeeklyAudit(vault_path='./AI_Employee_Vault')
activity = audit._gather_weekly_activity()
accounting = audit._gather_accounting_data()

# Custom analysis
print(f"Total actions: {len(activity)}")
print(f"Revenue: ${accounting['revenue']}")
```

## Related Skills

- **Odoo MCP Server** - Provides accounting data
- **Email MCP Server** - Send briefing notifications
- **Ralph Loop** - Automate audit execution

## Support

- 📚 **Documentation:** This file
- 🐛 **Issues:** Check logs in Logs/ folder
- 💬 **Community:** Wednesday Research Meetings

---

**Built for Gold Tier - FTE AI Employee Hackathon**  
**Transforms data into actionable business intelligence**
