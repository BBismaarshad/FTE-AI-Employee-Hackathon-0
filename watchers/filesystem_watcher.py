"""
Filesystem Watcher - Monitors a drop folder for new files.

When files are dropped into the monitored folder, this watcher:
1. Detects the new file
2. Copies it to the vault's Needs_Action folder
3. Creates a metadata .md file describing the dropped file

Usage:
    python filesystem_watcher.py --vault /path/to/vault --drop /path/to/drop_folder
"""

import os
import sys
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher, setup_logging


class FilesystemWatcher(BaseWatcher):
    """Watches a drop folder for new files and creates action files in the vault."""

    def __init__(self, vault_path: str, drop_folder: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.drop_folder = Path(drop_folder)
        self.processed_files = set()

        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)

        # Load previously processed files (for restart persistence)
        self._load_processed_files()

    def _load_processed_files(self):
        """Load list of already processed files from state file."""
        state_file = self.vault_path / '.state' / 'filesystem_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            self.processed_files = set(state_file.read_text().splitlines())

    def _save_processed_files(self):
        """Save list of processed files for restart persistence."""
        state_file = self.vault_path / '.state' / 'filesystem_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text('\n'.join(self.processed_files))

    def check_for_updates(self) -> list:
        """
        Check drop folder for new files.

        Returns:
            list: List of new file paths
        """
        new_files = []

        if not self.drop_folder.exists():
            return new_files

        for filepath in self.drop_folder.iterdir():
            if filepath.is_file():
                file_key = str(filepath.resolve())
                if file_key not in self.processed_files:
                    new_files.append(filepath)

        return new_files

    def create_action_file(self, file_path: Path) -> Path:
        """
        Create action file for a dropped file.

        Args:
            file_path: Path to the dropped file

        Returns:
            Path: Path to the created action file
        """
        # Copy file to vault
        dest_path = self.vault_path / 'Inbox' / file_path.name
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest_path)

        # Get file metadata
        file_size = file_path.stat().st_size
        file_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

        # Create action file
        action_filename = f'FILE_{file_path.stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        action_path = self.needs_action / action_filename

        content = f"""---
type: file_drop
original_name: {file_path.name}
original_path: {file_path.resolve()}
copied_to: {dest_path}
size: {file_size} bytes
modified: {file_modified}
received: {datetime.now().isoformat()}
status: pending
---

# File Drop: {file_path.name}

## Details
- **Original Location**: `{file_path.resolve()}`
- **Copied To**: `{dest_path}`
- **File Size**: {file_size} bytes ({file_size / 1024:.1f} KB)
- **Last Modified**: {file_modified}

## Action Required
A new file has been dropped for processing. Review the file and take appropriate action.

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize and file in appropriate vault folder
- [ ] Take action based on file content
- [ ] Move to /Done when complete

---
*Detected by Filesystem Watcher at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        action_path.write_text(content)

        # Mark as processed
        self.processed_files.add(str(file_path.resolve()))
        self._save_processed_files()

        return action_path


def main():
    parser = argparse.ArgumentParser(description='Filesystem Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--drop', type=str, default='drop_folder',
                        help='Path to drop folder (default: ./drop_folder)')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for testing/scheduled tasks)')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('FilesystemWatcher')

    # Create watcher
    watcher = FilesystemWatcher(
        vault_path=args.vault,
        drop_folder=args.drop,
        check_interval=args.interval
    )

    if args.once:
        # Run single check (for testing or scheduled tasks)
        count = watcher.run_once()
        logger.info(f'Filesystem watcher created {count} action files')
    else:
        # Run continuously
        logger.info(f'Monitoring: {args.drop}')
        logger.info(f'Vault: {args.vault}')
        logger.info(f'Interval: {args.interval}s')
        try:
            watcher.run()
        except KeyboardInterrupt:
            logger.info('Filesystem watcher stopped by user')


if __name__ == '__main__':
    main()
