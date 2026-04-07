"""
LinkedIn Approval Handler - Integrates with orchestrator for automated posting.

This handler:
1. Monitors Approved/LinkedIn folder for approved posts
2. Executes posting via LinkedInPoster
3. Moves completed posts to Done/LinkedIn
4. Logs all operations for audit trail

Usage:
    # Called by orchestrator when it detects approved posts
    python skills/linkedin_approval_handler.py --vault ./AI_Employee_Vault

    # Manual execution of approved posts
    python skills/linkedin_approval_handler.py --vault ./AI_Employee_Vault --execute
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import setup_logging
from linkedin_poster import LinkedInPoster


class LinkedInApprovalHandler:
    """Handles approval workflow for LinkedIn posts."""

    def __init__(self, vault_path: str, headless: bool = False):
        self.vault_path = Path(vault_path)
        self.headless = headless

        # Folders
        self.pending_approval = self.vault_path / 'Pending_Approval' / 'LinkedIn'
        self.approved_folder = self.vault_path / 'Approved' / 'LinkedIn'
        self.rejected_folder = self.vault_path / 'Rejected' / 'LinkedIn'
        self.done_folder = self.vault_path / 'Done' / 'LinkedIn'
        self.drafts_folder = self.vault_path / 'Drafts' / 'LinkedIn'
        self.logs_folder = self.vault_path / 'Logs'

        # Ensure folders exist
        for folder in [self.pending_approval, self.approved_folder,
                       self.rejected_folder, self.done_folder,
                       self.drafts_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Logger
        self.logger = logging.getLogger('LinkedInApprovalHandler')

        # Create poster instance
        self.poster = LinkedInPoster(
            vault_path=str(vault_path),
            headless=headless
        )

    def check_pending_approvals(self) -> list:
        """
        Check for pending approval requests.

        Returns:
            list: List of approval file paths
        """
        if not self.pending_approval.exists():
            return []

        return list(self.pending_approval.glob('POST_*.md'))

    def check_approved_posts(self) -> list:
        """
        Check for approved posts ready to publish.

        Returns:
            list: List of approved file paths
        """
        if not self.approved_folder.exists():
            return []

        return list(self.approved_folder.glob('POST_*.md'))

    def execute_approved_posts(self) -> dict:
        """
        Execute all approved posts.

        Returns:
            dict: Results with success/failed counts
        """
        approved_posts = self.check_approved_posts()

        if not approved_posts:
            self.logger.info('No approved posts found')
            return {'success': 0, 'failed': 0, 'total': 0}

        self.logger.info(f'Found {len(approved_posts)} approved post(s) to publish')

        results = {'success': 0, 'failed': 0, 'total': len(approved_posts)}

        for approval_file in approved_posts:
            try:
                self.logger.info(f'Processing: {approval_file.name}')

                # Read approval file
                content = approval_file.read_text(encoding='utf-8')

                # Extract draft file reference
                draft_file_name = None
                for line in content.split('\n')[:20]:
                    if line.startswith('draft_file:'):
                        draft_file_name = line.split(':', 1)[1].strip()
                        break

                if not draft_file_name:
                    self.logger.warning(f'No draft file reference in {approval_file.name}')
                    results['failed'] += 1
                    continue

                # Find draft file
                draft_path = self.drafts_folder / draft_file_name
                if not draft_path.exists():
                    self.logger.error(f'Draft file not found: {draft_file_name}')
                    results['failed'] += 1
                    continue

                # Read draft and extract post content
                draft_content = draft_path.read_text(encoding='utf-8')
                post_text = self.poster._extract_post_content(draft_content)

                if not post_text:
                    self.logger.error(f'Could not extract post content from {draft_file_name}')
                    results['failed'] += 1
                    continue

                # Post to LinkedIn
                success = self.poster.post_to_linkedin(post_text)

                # Log the operation
                self._log_execution({
                    'approval_file': approval_file.name,
                    'draft_file': draft_file_name,
                    'text_preview': post_text[:100],
                    'timestamp': datetime.now().isoformat(),
                    'success': success
                })

                if success:
                    # Move to Done
                    dest = self.done_folder / approval_file.name
                    approval_file.rename(dest)
                    self.logger.info(f'✅ Published: {draft_file_name}')
                    results['success'] += 1
                else:
                    self.logger.error(f'❌ Failed to publish: {draft_file_name}')
                    results['failed'] += 1

            except Exception as e:
                self.logger.error(f'Error processing {approval_file.name}: {e}')
                results['failed'] += 1

        # Summary
        self.logger.info(f'')
        self.logger.info(f'LinkedIn Posting Summary:')
        self.logger.info(f'  Total: {results["total"]}')
        self.logger.info(f'  Published: {results["success"]}')
        self.logger.info(f'  Failed: {results["failed"]}')
        self.logger.info(f'')

        return results

    def _log_execution(self, data: dict):
        """Log execution details."""
        log_file = self.logs_folder / 'linkedin_posting_log.json'

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []

        # Add new entry
        logs.append(data)

        # Write back
        log_file.write_text(json.dumps(logs, indent=2))

    def run_cycle(self) -> dict:
        """
        Run a single approval cycle.

        Checks for approved posts and executes them.

        Returns:
            dict: Results
        """
        self.logger.info('Running LinkedIn approval cycle...')

        # Check pending approvals (informational)
        pending = self.check_pending_approvals()
        if pending:
            self.logger.info(f'{len(pending)} post(s) awaiting approval')

        # Execute approved posts
        results = self.execute_approved_posts()

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Approval Handler')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--execute', action='store_true',
                        help='Execute approved posts')
    parser.add_argument('--check', action='store_true',
                        help='Check approval status')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('LinkedInApprovalHandler')

    try:
        handler = LinkedInApprovalHandler(
            vault_path=args.vault,
            headless=args.headless
        )

        if args.check:
            # Check status
            pending = handler.check_pending_approvals()
            approved = handler.check_approved_posts()

            print(f'LinkedIn Approval Status:')
            print(f'  Pending Approval: {len(pending)}')
            print(f'  Approved (Ready to Post): {len(approved)}')
            print(f'')

            if pending:
                print(f'Pending Posts:')
                for p in pending:
                    print(f'  - {p.name}')
                print(f'')

            if approved:
                print(f'Approved Posts:')
                for a in approved:
                    print(f'  - {a.name}')
                print(f'')
                print(f'Run with --execute to publish these posts')

            sys.exit(0)

        elif args.execute:
            # Execute approved posts
            results = handler.execute_approved_posts()

            if results['success'] > 0:
                print(f'✅ Published {results["success"]} post(s)')
                if results['failed'] > 0:
                    print(f'⚠️  {results["failed"]} post(s) failed')
                sys.exit(0)
            else:
                print(f'⚠️  No posts were published')
                sys.exit(1)

        else:
            # Default: run one cycle
            results = handler.run_cycle()

            if results['success'] > 0:
                print(f'✅ Published {results["success"]} post(s)')
                sys.exit(0)
            else:
                print(f'⚠️  No posts to publish')
                print(f'   Check status with: --check')
                print(f'   Execute manually with: --execute')
                sys.exit(1)

    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
