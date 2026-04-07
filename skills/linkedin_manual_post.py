"""
LinkedIn Manual Post Helper - Opens draft and LinkedIn for easy manual posting.

This script:
1. Reads the approved LinkedIn post draft
2. Copies the content to clipboard
3. Opens LinkedIn in your browser
4. You just paste and click "Post"!

Usage:
    python skills/linkedin_manual_post.py --vault ./AI_Employee_Vault
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import setup_logging
import webbrowser


class LinkedInManualPoster:
    """Helper for manual LinkedIn posting."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved' / 'LinkedIn'
        self.drafts_folder = self.vault_path / 'Drafts' / 'LinkedIn'
        self.done_folder = self.vault_path / 'Done' / 'LinkedIn'
        self.pending_folder = self.vault_path / 'Pending_Approval' / 'LinkedIn'
        
        self.logger = logging.getLogger('LinkedInManualPoster')

    def _extract_post_content(self, content: str) -> str:
        """Extract the actual post content from a draft/approval file."""
        try:
            # Look for "## Content" section
            if '## Content' in content:
                parts = content.split('## Content', 1)
                if len(parts) > 1:
                    content_part = parts[1]
                    if '## Metadata' in content_part:
                        content_part = content_part.split('## Metadata')[0]
                    return content_part.strip()
            return ''
        except Exception as e:
            self.logger.error(f'Error extracting post content: {e}')
            return ''

    def post_manual(self) -> bool:
        """
        Open approved post content and LinkedIn for manual posting.
        
        Returns:
            bool: True if a post was found and opened
        """
        self.logger.info('Looking for approved LinkedIn posts...')

        # Check approved folder first
        approved_files = []
        if self.approved_folder.exists():
            approved_files = list(self.approved_folder.glob('POST_*.md'))
        
        # If no approved, check pending
        if not approved_files and self.pending_folder.exists():
            approved_files = list(self.pending_folder.glob('POST_*.md'))
            if approved_files:
                self.logger.info('No approved posts found, checking pending...')

        if not approved_files:
            self.logger.warning('No posts found to publish')
            return False

        # Process the first approved/pending file
        approval_file = approved_files[0]
        self.logger.info(f'Processing: {approval_file.name}')

        try:
            content = approval_file.read_text(encoding='utf-8')
            
            # Extract draft file reference
            draft_file_name = None
            for line in content.split('\n')[:20]:
                if line.startswith('draft_file:'):
                    draft_file_name = line.split(':', 1)[1].strip()
                    break

            # Extract post content
            post_text = ''
            if draft_file_name:
                draft_path = self.drafts_folder / draft_file_name
                if draft_path.exists():
                    draft_content = draft_path.read_text(encoding='utf-8')
                    post_text = self._extract_post_content(draft_content)
            
            # If no draft reference, try to extract from approval file itself
            if not post_text:
                post_text = self._extract_post_content(content)

            if not post_text:
                self.logger.error('Could not extract post content')
                return False

            # Display the post
            print('\n' + '='*60)
            print('📝 LINKEDIN POST READY TO PUBLISH')
            print('='*60)
            print(post_text)
            print('='*60)
            print('\n')

            # Copy to clipboard using Python
            try:
                import pyperclip
                pyperclip.copy(post_text)
                self.logger.info('✅ Post content copied to clipboard!')
                print('✅ Post content copied to clipboard!')
            except ImportError:
                # Fallback: use Windows clipboard command
                import subprocess
                subprocess.run(['clip'], input=post_text.encode('utf-8'), shell=True)
                self.logger.info('✅ Post content copied to clipboard!')
                print('✅ Post content copied to clipboard!')

            print('\n🚀 Opening LinkedIn in your browser...')
            print('   The post composer will open - just paste and post!')
            print('\n⏱️  Opening LinkedIn in 3 seconds...')
            time.sleep(3)

            # Open LinkedIn post composer
            webbrowser.open('https://www.linkedin.com/feed/')
            
            print('\n✅ LinkedIn opened! Instructions:')
            print('   1. Click "Start a post" or the compose box')
            print('   2. Press Ctrl+V to paste (content is already copied)')
            print('   3. Review and click "Post"')
            print(f'\n📄 Post source: {approval_file.name}')
            
            # Ask if user wants to mark as done
            print('\n' + '-'*60)
            mark_done = input('Did you publish the post? (y/n): ').strip().lower()
            
            if mark_done == 'y':
                # Move to done folder
                if approval_file.parent == self.approved_folder:
                    self.done_folder.mkdir(parents=True, exist_ok=True)
                    approval_file.rename(self.done_folder / approval_file.name)
                    self.logger.info(f'✅ Moved {approval_file.name} to Done')
                    print(f'✅ Moved to Done folder')
                elif approval_file.parent == self.pending_folder:
                    self.done_folder.mkdir(parents=True, exist_ok=True)
                    approval_file.rename(self.done_folder / f"DONE_{approval_file.name}")
                    self.logger.info(f'✅ Moved {approval_file.name} to Done')
                    print(f'✅ Moved to Done folder')
            else:
                print(f'⏸️  Keeping {approval_file.name} in {approval_file.parent.name}')
                print('   You can try again later with --manual')

            return True

        except Exception as e:
            self.logger.error(f'Error processing {approval_file.name}: {e}', exc_info=True)
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='LinkedIn Manual Post Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Open approved post for manual publishing
  python skills/linkedin_manual_post.py --vault ./AI_Employee_Vault
        '''
    )

    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('LinkedInManualPoster')

    try:
        poster = LinkedInManualPoster(vault_path=args.vault)
        success = poster.post_manual()
        
        if success:
            print('\n✅ Manual posting workflow completed!')
            sys.exit(0)
        else:
            print('\n⚠️  No posts found to publish')
            sys.exit(1)

    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
