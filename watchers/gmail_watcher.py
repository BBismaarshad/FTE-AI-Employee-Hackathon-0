"""
Gmail Watcher - Monitors Gmail for unread/important emails.

This watcher:
1. Authenticates using Google OAuth 2.0
2. Checks for unread messages periodically
3. Creates action files in Needs_Action folder for each new email
4. Tracks processed emails to avoid duplicates

Usage:
    python gmail_watcher.py --vault /path/to/vault --credentials /path/to/credentials.json

Security Note:
    NEVER commit credentials or token files to version control.
    Add token.json and credentials files to .gitignore
"""

import os
import sys
import time
import logging
import pickle
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher, setup_logging

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import Message
from email.parser import BytesParser

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Watches Gmail for unread messages and creates action files."""

    def __init__(self, vault_path: str, credentials_path: str = None, 
                 token_path: str = None, check_interval: int = 120):
        super().__init__(vault_path, check_interval)

        # Set default paths if not provided
        if credentials_path is None:
            credentials_path = str(Path(__file__).parent.parent / 'credentials' / 'gmail_credentials.json')
        if token_path is None:
            token_path = str(Path(__file__).parent.parent / 'credentials' / 'gmail_token.json')

        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)

        # Ensure credentials directory exists
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

        # Gmail service
        self.service = None

        # Track processed email IDs
        self.processed_ids = set()
        self._load_processed_ids()

        # Authenticate on startup
        self._authenticate()

    def _load_processed_ids(self):
        """Load list of already processed email IDs."""
        state_file = self.vault_path / '.state' / 'gmail_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            try:
                self.processed_ids = set(state_file.read_text().splitlines())
                self.logger.info(f'Loaded {len(self.processed_ids)} processed email IDs')
            except Exception as e:
                self.logger.warning(f'Error loading processed IDs: {e}')
                self.processed_ids = set()

    def _save_processed_ids(self):
        """Save list of processed email IDs."""
        state_file = self.vault_path / '.state' / 'gmail_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Keep only last 1000 IDs to prevent file from growing too large
            ids_list = list(self.processed_ids)[-1000:]
            state_file.write_text('\n'.join(ids_list))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')

    def _authenticate(self):
        """Authenticate with Google OAuth 2.0."""
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token_file:
                    creds = pickle.load(token_file)
                self.logger.info('Loaded existing Gmail token')
            except Exception as e:
                self.logger.warning(f'Error loading token: {e}')
                creds = None

        # If there are no valid credentials, prompt user to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info('Refreshing expired Gmail token...')
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Gmail credentials file not found at: {self.credentials_path}\n'
                        'Please download OAuth 2.0 credentials from Google Cloud Console.'
                    )

                self.logger.info('Opening browser for Gmail authorization...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token_file:
                pickle.dump(creds, token_file)
            self.logger.info('Gmail token saved successfully')

        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info('Gmail service authenticated')

    def check_for_updates(self) -> list:
        """
        Check Gmail for unread messages.

        Returns:
            list: List of unread message metadata
        """
        if not self.service:
            self.logger.error('Gmail service not authenticated')
            return []

        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=50  # Limit to 50 messages per check
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)

            self.logger.info(f'Found {len(messages)} unread messages, {len(new_messages)} new')
            return new_messages

        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            # Try to re-authenticate on auth errors
            if error.resp.status == 401:
                self.logger.info('Re-authenticating...')
                self._authenticate()
            return []

    def _get_email_content(self, message_id: str) -> dict:
        """
        Get full email content by ID.

        Args:
            message_id: Gmail message ID

        Returns:
            dict: Email content and metadata
        """
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()

            # Extract headers
            headers = {}
            for header in msg['payload'].get('headers', []):
                headers[header['name']] = header['value']

            return {
                'id': msg['id'],
                'threadId': msg.get('threadId', ''),
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'snippet': msg.get('snippet', ''),
                'labelIds': msg.get('labelIds', [])
            }

        except HttpError as error:
            self.logger.error(f'Error getting email {message_id}: {error}')
            return None

    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for an unread email.

        Args:
            message: Message metadata from check_for_updates()

        Returns:
            Path: Path to the created action file
        """
        # Get full email content
        email_content = self._get_email_content(message['id'])
        if not email_content:
            return None

        # Determine priority based on labels and sender
        priority = 'normal'
        if 'IMPORTANT' in email_content.get('labelIds', []):
            priority = 'high'
        elif 'CATEGORY_PROMOTIONS' in email_content.get('labelIds', []):
            priority = 'low'

        # Create action file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_filename = f'EMAIL_{message["id"]}_{timestamp}.md'
        action_path = self.needs_action / action_filename

        content = f"""---
type: email
from: {email_content['from']}
to: {email_content['to']}
subject: {email_content['subject']}
received: {datetime.now().isoformat()}
message_id: {email_content['id']}
thread_id: {email_content.get('threadId', '')}
priority: {priority}
status: pending
---

# Email: {email_content['subject']}

## Metadata
- **From**: {email_content['from']}
- **To**: {email_content['to']}
- **Received**: {email_content['date']}
- **Message ID**: {email_content['id']}
- **Priority**: {priority}

## Preview
{email_content['snippet']}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply if action required
- [ ] Forward to relevant person/team
- [ ] Archive after processing

---
*Detected by Gmail Watcher at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        action_path.write_text(content)

        # Mark as processed
        self.processed_ids.add(message['id'])
        self._save_processed_ids()

        self.logger.info(f'Created action file for email: {email_content["subject"][:50]}')
        return action_path

    def mark_as_read(self, message_id: str):
        """
        Mark email as read after processing (optional).

        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f'Marked email {message_id} as read')
        except HttpError as error:
            self.logger.error(f'Error marking email as read: {error}')


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--credentials', type=str, default=None,
                        help='Path to Gmail credentials JSON file')
    parser.add_argument('--token', type=str, default=None,
                        help='Path to store Gmail token file')
    parser.add_argument('--interval', type=int, default=120,
                        help='Check interval in seconds (default: 120)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for testing/scheduled tasks)')
    parser.add_argument('--mark-read', action='store_true',
                        help='Mark emails as read after processing')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('GmailWatcher')

    try:
        # Create watcher
        watcher = GmailWatcher(
            vault_path=args.vault,
            credentials_path=args.credentials,
            token_path=args.token,
            check_interval=args.interval
        )

        if args.once:
            # Run single check
            count = watcher.run_once()
            logger.info(f'Gmail watcher created {count} action files')
        else:
            # Run continuously
            logger.info(f'Monitoring Gmail for unread messages')
            logger.info(f'Vault: {args.vault}')
            logger.info(f'Interval: {args.interval}s')
            try:
                watcher.run()
            except KeyboardInterrupt:
                logger.info('Gmail watcher stopped by user')

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
