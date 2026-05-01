"""
Weekly Business Audit - Gold Tier AI Employee Skill

Generates the Monday Morning CEO Briefing with:
- Business performance analysis vs goals
- Accounting transaction audit (from Odoo or local data)
- Bottleneck identification
- Proactive suggestions
- Revenue tracking

Part of the Gold Tier requirements for the FTE AI Employee Hackathon.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class WeeklyAudit:
    """Performs weekly business and accounting audits."""

    def __init__(self, vault_path, odoo_client=None):
        """
        Initialize Weekly Audit.

        Args:
            vault_path: Path to Obsidian vault
            odoo_client: Optional OdooMCP client for accounting data
        """
        self.vault_path = Path(vault_path)
        self.odoo_client = odoo_client
        self.logger = logging.getLogger('WeeklyAudit')

        # Vault folders
        self.goals_file = self.vault_path / 'Business_Goals.md'
        self.briefings_folder = self.vault_path / 'Briefings'
        self.logs_folder = self.vault_path / 'Logs'
        self.done_folder = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'

        # Create folders
        for folder in [self.briefings_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def run_audit(self) -> Path:
        """
        Run the full weekly audit and generate CEO briefing.

        Returns:
            Path to generated briefing file
        """
        self.logger.info("🔍 Starting weekly business audit...")

        # 1. Gather data
        goals = self._read_goals()
        activity = self._gather_weekly_activity()
        accounting = self._gather_accounting_data()
        bottlenecks = self._identify_bottlenecks()
        suggestions = self._generate_suggestions(goals, activity, accounting)

        # 2. Analyze performance
        summary = self._analyze_performance(goals, activity, accounting, bottlenecks, suggestions)

        # 3. Generate briefing
        briefing_path = self._generate_briefing(summary)

        self.logger.info(f"✅ Audit complete. Briefing: {briefing_path}")
        return briefing_path

    def _read_goals(self) -> str:
        """Read business goals from Obsidian vault."""
        if not self.goals_file.exists():
            self.logger.warning("No Business_Goals.md found")
            return "No business goals defined yet."

        try:
            return self.goals_file.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to read goals: {e}")
            return "Error reading goals."

    def _gather_weekly_activity(self) -> List[Dict]:
        """
        Gather completed tasks and logs from the last 7 days.

        Returns:
            List of activity entries
        """
        activity = []
        cutoff = datetime.now() - timedelta(days=7)

        # Check Done folder for completed tasks
        if self.done_folder.exists():
            for f in self.done_folder.rglob('*.md'):
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) > cutoff:
                        activity.append({
                            'type': 'completed_task',
                            'name': f.stem,
                            'date': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                            'folder': f.parent.name
                        })
                except:
                    pass

        # Check logs for actions
        if self.logs_folder.exists():
            for log_file in self.logs_folder.glob('*.json'):
                try:
                    # Parse date from filename (YYYY-MM-DD.json)
                    date_str = log_file.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')

                    if file_date > cutoff:
                        logs = json.loads(log_file.read_text(encoding='utf-8'))
                        for entry in logs:
                            activity.append({
                                'type': 'action',
                                'action_type': entry.get('action_type', 'unknown'),
                                'status': entry.get('status', 'unknown'),
                                'timestamp': entry.get('timestamp'),
                                'actor': entry.get('actor', 'unknown')
                            })
                except Exception as e:
                    self.logger.debug(f"Skipping log file {log_file}: {e}")

        self.logger.info(f"Gathered {len(activity)} activity entries")
        return activity

    def _gather_accounting_data(self) -> Dict:
        """
        Gather accounting data from Odoo or local sources.

        Returns:
            dict with financial metrics
        """
        if self.odoo_client:
            try:
                # Get data from Odoo
                summary = self.odoo_client.get_account_summary()
                invoices = self.odoo_client.get_recent_invoices(limit=20)

                if summary.get('success') and invoices.get('success'):
                    # Calculate revenue from posted invoices
                    revenue = sum(
                        inv['amount_total']
                        for inv in invoices.get('invoices', [])
                        if inv.get('state') == 'posted'
                    )

                    return {
                        'revenue': revenue,
                        'receivable': summary.get('total_receivable', 0),
                        'payable': summary.get('total_payable', 0),
                        'net_balance': summary.get('net_balance', 0),
                        'pending_invoices': len([
                            inv for inv in invoices.get('invoices', [])
                            if inv.get('state') == 'draft'
                        ]),
                        'source': 'odoo'
                    }
            except Exception as e:
                self.logger.error(f"Failed to get Odoo data: {e}")

        # Fallback: analyze from logs
        revenue = 0
        expenses = 0

        if self.logs_folder.exists():
            cutoff = datetime.now() - timedelta(days=7)
            for log_file in self.logs_folder.glob('*.json'):
                try:
                    date_str = log_file.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')

                    if file_date > cutoff:
                        logs = json.loads(log_file.read_text(encoding='utf-8'))
                        for entry in logs:
                            if entry.get('action_type') == 'create_invoice':
                                revenue += entry.get('amount', 0)
                            elif entry.get('action_type') == 'create_payment':
                                if entry.get('type') == 'outbound':
                                    expenses += entry.get('amount', 0)
                except:
                    pass

        return {
            'revenue': revenue,
            'expenses': expenses,
            'net_balance': revenue - expenses,
            'pending_invoices': 0,
            'source': 'logs'
        }

    def _identify_bottlenecks(self) -> List[Dict]:
        """
        Identify bottlenecks in workflow.

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        # Check for stale items in Needs_Action
        if self.needs_action.exists():
            cutoff = datetime.now() - timedelta(days=3)
            stale_count = 0

            for f in self.needs_action.glob('*.md'):
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                        stale_count += 1
                except:
                    pass

            if stale_count > 0:
                bottlenecks.append({
                    'type': 'stale_tasks',
                    'count': stale_count,
                    'description': f'{stale_count} tasks in Needs_Action older than 3 days',
                    'severity': 'medium'
                })

        # Check for incomplete plans
        if self.plans_folder.exists():
            incomplete_plans = 0
            for f in self.plans_folder.glob('*.md'):
                try:
                    content = f.read_text(encoding='utf-8')
                    if '- [ ]' in content:  # Has unchecked items
                        incomplete_plans += 1
                except:
                    pass

            if incomplete_plans > 5:
                bottlenecks.append({
                    'type': 'incomplete_plans',
                    'count': incomplete_plans,
                    'description': f'{incomplete_plans} plans with incomplete tasks',
                    'severity': 'high'
                })

        return bottlenecks

    def _generate_suggestions(self, goals: str, activity: List[Dict], accounting: Dict) -> List[str]:
        """
        Generate proactive suggestions based on data.

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Revenue-based suggestions
        revenue = accounting.get('revenue', 0)
        if revenue == 0:
            suggestions.append("💡 No revenue recorded this week. Consider reviewing sales pipeline and follow-ups.")
        elif revenue > 5000:
            suggestions.append(f"🎉 Strong revenue week (${revenue:.2f})! Consider scaling successful strategies.")

        # Pending invoices
        pending = accounting.get('pending_invoices', 0)
        if pending > 3:
            suggestions.append(f"📋 {pending} draft invoices pending. Shall I prepare them for review?")

        # Activity level
        completed_tasks = len([a for a in activity if a.get('type') == 'completed_task'])
        if completed_tasks < 5:
            suggestions.append("📊 Low task completion this week. Consider reviewing priorities and blockers.")
        elif completed_tasks > 20:
            suggestions.append(f"🚀 High productivity week ({completed_tasks} tasks completed)! Great momentum.")

        # Social media activity
        social_posts = len([a for a in activity if 'post' in a.get('action_type', '').lower()])
        if social_posts == 0:
            suggestions.append("📱 No social media posts this week. Consider scheduling content for engagement.")

        # Email activity
        emails_sent = len([a for a in activity if a.get('action_type') == 'email_send'])
        if emails_sent > 50:
            suggestions.append(f"📧 High email volume ({emails_sent} sent). Consider templates for common responses.")

        return suggestions

    def _analyze_performance(self, goals: str, activity: List[Dict],
                           accounting: Dict, bottlenecks: List[Dict],
                           suggestions: List[str]) -> Dict:
        """
        Analyze overall performance and create summary.

        Returns:
            dict with analysis results
        """
        # Calculate metrics
        completed_count = len([a for a in activity if a.get('type') == 'completed_task'])
        action_count = len([a for a in activity if a.get('type') == 'action'])

        # Determine trend
        revenue = accounting.get('revenue', 0)
        if revenue > 3000:
            trend = "Strong"
        elif revenue > 1000:
            trend = "Moderate"
        else:
            trend = "Needs attention"

        return {
            'period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            'revenue': accounting.get('revenue', 0),
            'expenses': accounting.get('expenses', 0),
            'net_balance': accounting.get('net_balance', 0),
            'receivable': accounting.get('receivable', 0),
            'payable': accounting.get('payable', 0),
            'completed_count': completed_count,
            'action_count': action_count,
            'activity_summary': activity[:10],  # Top 10
            'bottlenecks': bottlenecks,
            'suggestions': suggestions,
            'trend': trend,
            'data_source': accounting.get('source', 'unknown')
        }

    def _generate_briefing(self, summary: Dict) -> Path:
        """
        Create the Monday Morning CEO Briefing markdown file.

        Args:
            summary: Analysis summary dict

        Returns:
            Path to created briefing file
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_str}_Monday_CEO_Briefing.md"
        filepath = self.briefings_folder / filename

        content = f"""---
generated: {datetime.now().isoformat()}
type: ceo_briefing
period: {summary['period']}
trend: {summary['trend']}
data_source: {summary['data_source']}
---

# 📊 Monday Morning CEO Briefing

**Period:** {summary['period']}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 🎯 Executive Summary

Business performance is **{summary['trend']}** this week. {summary['completed_count']} tasks completed with {summary['action_count']} automated actions executed.

---

## 💰 Financial Performance

| Metric | Amount |
|--------|--------|
| **Revenue** | ${summary['revenue']:.2f} |
| **Expenses** | ${summary['expenses']:.2f} |
| **Net Balance** | ${summary['net_balance']:.2f} |
| **Accounts Receivable** | ${summary['receivable']:.2f} |
| **Accounts Payable** | ${summary['payable']:.2f} |

**Data Source:** {summary['data_source'].title()}

---

## ✅ Completed Activities

**Total Completed:** {summary['completed_count']} tasks
**Automated Actions:** {summary['action_count']} actions

### Recent Highlights
"""

        # Add activity highlights
        for i, activity in enumerate(summary['activity_summary'][:5], 1):
            if activity.get('type') == 'completed_task':
                content += f"{i}. ✓ {activity.get('name', 'Unknown task')} ({activity.get('folder', 'General')})\n"
            elif activity.get('type') == 'action':
                content += f"{i}. 🤖 {activity.get('action_type', 'Unknown')} - {activity.get('status', 'unknown')}\n"

        content += "\n---\n\n## 🚧 Bottlenecks & Issues\n\n"

        if summary['bottlenecks']:
            for bottleneck in summary['bottlenecks']:
                severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(bottleneck.get('severity', 'low'), '⚪')
                content += f"- {severity_emoji} **{bottleneck.get('type', 'Unknown').replace('_', ' ').title()}**: {bottleneck.get('description', 'No description')}\n"
        else:
            content += "✅ No significant bottlenecks identified this week.\n"

        content += "\n---\n\n## 💡 Proactive Suggestions\n\n"

        if summary['suggestions']:
            for suggestion in summary['suggestions']:
                content += f"- {suggestion}\n"
        else:
            content += "- Continue current operations. All systems running smoothly.\n"

        content += f"""

---

## 📈 Next Week Focus

Based on this week's performance, consider:

1. **Follow up on pending items** in Needs_Action folder
2. **Review and approve** any pending invoices or payments
3. **Engage with social media** posts and comments
4. **Monitor** accounts receivable for timely collections

---

## 📋 Action Items

- [ ] Review this briefing
- [ ] Address high-priority bottlenecks
- [ ] Approve pending financial transactions
- [ ] Update Business_Goals.md if needed

---

*🤖 Generated by AI Employee - Weekly Audit System*
*For questions or adjustments, review the audit configuration in `skills/weekly_audit.py`*
"""

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"✅ Briefing saved to {filepath}")

        return filepath


def main():
    """CLI interface for Weekly Audit."""
    parser = argparse.ArgumentParser(description='Weekly Business Audit - Gold Tier AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--odoo-url', type=str, help='Odoo server URL')
    parser.add_argument('--odoo-db', type=str, help='Odoo database name')
    parser.add_argument('--odoo-user', type=str, help='Odoo username')
    parser.add_argument('--odoo-password', type=str, help='Odoo password')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize Odoo client if credentials provided
    odoo_client = None
    if args.odoo_url and args.odoo_db and args.odoo_user:
        try:
            from skills.odoo_mcp import OdooMCP
            password = args.odoo_password or os.getenv('ODOO_PASSWORD', 'admin')
            odoo_client = OdooMCP(
                url=args.odoo_url,
                db=args.odoo_db,
                username=args.odoo_user,
                password=password,
                vault_path=args.vault
            )
            print("✅ Connected to Odoo for accounting data")
        except Exception as e:
            print(f"⚠️  Could not connect to Odoo: {e}")
            print("📊 Will use log-based accounting data instead")

    # Run audit
    audit = WeeklyAudit(vault_path=args.vault, odoo_client=odoo_client)

    print("\n" + "="*60)
    print("🔍 WEEKLY BUSINESS AUDIT")
    print("="*60 + "\n")

    briefing_path = audit.run_audit()

    print("\n" + "="*60)
    print(f"✅ CEO Briefing generated: {briefing_path}")
    print("="*60)
    print("\n📖 Open the briefing in Obsidian to review this week's performance.")


if __name__ == '__main__':
    main()
