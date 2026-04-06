"""
Orchestrator - Master process that manages the AI Employee.

Responsibilities:
1. Monitor Needs_Action folder for new action files
2. Trigger Qwen Code to process action files
3. Move completed files to Done folder
4. Update Dashboard.md with recent activity
5. Manage watcher processes
6. Handle approval workflow

Usage:
    python orchestrator.py --vault /path/to/vault [--qwen-path /path/to/qwen]
"""

import os
import sys
import json
import time
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add watchers directory to path
sys.path.insert(0, str(Path(__file__).parent / 'watchers'))

from base_watcher import setup_logging


class Orchestrator:
    """Master orchestrator for AI Employee system."""

    def __init__(self, vault_path: str, qwen_command: str = 'qwen'):
        self.vault_path = Path(vault_path)
        self.qwen_command = qwen_command

        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure all folders exist
        for folder in [self.needs_action, self.done, self.plans,
                       self.pending_approval, self.approved, self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.processed_files = set()
        self._load_state()

        # Logger
        self.logger = logging.getLogger('Orchestrator')

    def _load_state(self):
        """Load processed files state for restart persistence."""
        state_file = self.vault_path / '.state' / 'orchestrator.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            self.processed_files = set(state_file.read_text().splitlines())

    def _save_state(self):
        """Save processed files state."""
        state_file = self.vault_path / '.state' / 'orchestrator.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text('\n'.join(self.processed_files))

    def get_pending_actions(self) -> list:
        """
        Get list of pending action files.

        Returns:
            list: Paths to action files in Needs_Action folder
        """
        if not self.needs_action.exists():
            return []

        action_files = []
        for filepath in self.needs_action.glob('*.md'):
            if str(filepath.resolve()) not in self.processed_files:
                action_files.append(filepath)

        return sorted(action_files, key=lambda f: f.stat().st_mtime)

    def process_action_file(self, action_path: Path) -> bool:
        """
        Process a single action file.

        For Bronze tier: Read the file, create a plan, and prepare for Qwen Code processing.

        Args:
            action_path: Path to the action file

        Returns:
            bool: True if processing succeeded
        """
        self.logger.info(f'Processing: {action_path.name}')

        try:
            # Read action file
            content = action_path.read_text()

            # Extract metadata from frontmatter
            metadata = self._parse_frontmatter(content)

            # Create a plan file for Claude
            plan_path = self._create_plan(action_path, metadata)

            # Log the action
            self._log_action(action_path, metadata, 'plan_created')

            # Move to processed (not done yet - Claude needs to work on it)
            self.processed_files.add(str(action_path.resolve()))
            self._save_state()

            # Update dashboard
            self._update_dashboard(action_path, 'planned', metadata)

            self.logger.info(f'Plan created: {plan_path.name}')
            return True

        except Exception as e:
            self.logger.error(f'Error processing {action_path.name}: {e}', exc_info=True)
            return False

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown content."""
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                lines = parts[1].strip().split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        return metadata

    def _create_plan(self, action_path: Path, metadata: dict) -> Path:
        """Create a plan file for Qwen Code to process."""
        plan_name = f'PLAN_{action_path.stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        plan_path = self.plans / plan_name

        action_type = metadata.get('type', 'unknown')

        plan_content = f"""---
created: {datetime.now().isoformat()}
status: pending
action_file: {action_path.name}
action_type: {action_type}
---

# Plan: {action_path.stem.replace('_', ' ').title()}

## Objective
Process the action file: `{action_path.name}`

## Action Details
"""
        for key, value in metadata.items():
            plan_content += f"- **{key}**: {value}\n"

        plan_content += f"""

## Steps
- [ ] Review action file contents
- [ ] Determine appropriate response
- [ ] Execute required actions
- [ ] Update dashboard with results
- [ ] Move action file to /Done when complete

## Notes
_Add any additional notes here_

---
*Created by Orchestrator at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        plan_path.write_text(plan_content)
        return plan_path

    def _log_action(self, action_path: Path, metadata: dict, status: str):
        """Log action to daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_file': action_path.name,
            'action_type': metadata.get('type', 'unknown'),
            'status': status,
            'result': 'plan_created'
        }

        # Load existing logs or create new
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def _update_dashboard(self, action_path: Path, status: str, metadata: dict):
        """Update Dashboard.md with recent activity."""
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found, creating new one')
            return

        content = self.dashboard.read_text()

        # Add activity entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        activity_line = f'- [{timestamp}] {status}: {action_path.name}'

        # Find Recent Activity section and add entry
        if '## Recent Activity' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line == '## Recent Activity':
                    # Insert after the header
                    lines.insert(i + 1, activity_line)
                    break
            content = '\n'.join(lines)
        else:
            content += f'\n## Recent Activity\n{activity_line}\n'

        self.dashboard.write_text(content)

    def mark_complete(self, action_path: Path) -> bool:
        """
        Mark an action as complete and move to Done folder.

        Args:
            action_path: Path to the action file in Needs_Action

        Returns:
            bool: True if moved successfully
        """
        try:
            dest_path = self.done / action_path.name
            shutil.move(str(action_path), str(dest_path))

            # Update plan status
            plan_name = f'PLAN_{action_path.stem}_*.md'
            for plan_file in self.plans.glob(f'PLAN_{action_path.stem}_*.md'):
                content = plan_file.read_text()
                content = content.replace('status: pending', 'status: completed')
                plan_file.write_text(content)

            # Update dashboard
            self._update_dashboard(action_path, 'completed', {})

            self.logger.info(f'Completed: {action_path.name} -> {dest_path.name}')
            return True

        except Exception as e:
            self.logger.error(f'Error completing {action_path.name}: {e}', exc_info=True)
            return False

    def process_pending(self) -> int:
        """
        Process all pending action files.

        Returns:
            int: Number of files processed
        """
        pending = self.get_pending_actions()
        count = 0

        for action_path in pending:
            if self.process_action_file(action_path):
                count += 1

        return count

    def get_pending_approvals(self) -> list:
        """Get list of files awaiting human approval."""
        if not self.pending_approval.exists():
            return []
        return list(self.pending_approval.glob('*.md'))

    def get_approved(self) -> list:
        """Get list of recently approved files."""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))

    def run_cycle(self):
        """Run a single orchestration cycle."""
        self.logger.info('Running orchestration cycle...')

        # Process pending actions
        processed = self.process_pending()
        if processed > 0:
            self.logger.info(f'Processed {processed} action(s)')

        # Check for approvals (for future tiers)
        approved = self.get_approved()
        if approved:
            self.logger.info(f'{len(approved)} approved action(s) ready for execution')

        # Log summary
        pending = len(self.get_pending_actions())
        self.logger.info(f'Pending: {pending}, Approved: {len(approved)}')


def main():
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=60,
                        help='Cycle interval in seconds (default: 60)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for testing/scheduled tasks)')
    parser.add_argument('--qwen', type=str, default='qwen',
                        help='Qwen Code command (default: qwen)')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('Orchestrator')

    # Create orchestrator
    orchestrator = Orchestrator(
        vault_path=args.vault,
        qwen_command=args.qwen
    )

    if args.once:
        # Run single cycle
        count = orchestrator.process_pending()
        logger.info(f'Processed {count} action file(s)')
    else:
        # Run continuously
        logger.info(f'Vault: {args.vault}')
        logger.info(f'Interval: {args.interval}s')
        logger.info('Starting orchestration loop...')
        try:
            while True:
                orchestrator.run_cycle()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info('Orchestrator stopped by user')


if __name__ == '__main__':
    main()
