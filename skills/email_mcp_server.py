"""
Gmail MCP Server - MCP server for sending emails via Gmail API.

This MCP server provides tools for:
- Sending emails
- Creating drafts
- Validating addresses
- Rate limiting and audit logging

Usage:
    python skills/email_mcp_server.py --credentials ./credentials.json

Security:
    - Uses Gmail API with OAuth 2.0
    - Supports dry-run mode for testing
    - Rate limiting prevents accidental spam
    - All actions logged for audit
"""

import os
import sys
import json
import time
import pickle
import logging
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        'Google API client not installed. Run:\n'
        '  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib'
    )

# Scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly'
]


class EmailMCPServer:
    """MCP server for email operations."""

    def __init__(self, credentials_path: str, token_path: str = None,
                 dry_run: bool = False, max_per_hour: int = 10,
                 max_per_day: int = 50, cooldown_seconds: int = 30,
                 vault_path: str = None):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else \
            self.credentials_path.parent / 'token.json'

        self.dry_run = dry_run
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.cooldown_seconds = cooldown_seconds

        # Vault path for logging
        self.vault_path = Path(vault_path) if vault_path else \
            self.credentials_path.parent / 'AI_Employee_Vault'
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)

        # Gmail service
        self.service = None

        # Rate limiting
        self.send_log = []
        self.last_send_time = None

        # Logger
        self.logger = logging.getLogger('EmailMCP')

        # Load send log
        self._load_send_log()

        # Authenticate
        self._authenticate()

    def _load_send_log(self):
        """Load email send log for rate limiting."""
        log_file = self.logs_folder / 'email_operations.json'
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                # Keep only last 24 hours
                cutoff = datetime.now() - timedelta(hours=24)
                self.send_log = [
                    entry for entry in logs
                    if datetime.fromisoformat(entry['timestamp']) > cutoff
                ]
            except (json.JSONDecodeError, ValueError):
                self.send_log = []

    def _save_send_log(self, log_entry: dict):
        """Append to send log."""
        log_file = self.logs_folder / 'email_operations.json'

        # Load existing logs
        existing_logs = []
        if log_file.exists():
            try:
                existing_logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                existing_logs = []

        existing_logs.append(log_entry)
        log_file.write_text(json.dumps(existing_logs, indent=2))

    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as f:
                    creds = pickle.load(f)
                self.logger.info('Loaded existing Gmail token')
            except Exception:
                creds = None

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info('Refreshing expired Gmail token...')
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Gmail credentials not found at: {self.credentials_path}'
                    )

                self.logger.info('Opening browser for Gmail authorization...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

                with open(self.token_path, 'wb') as f:
                    pickle.dump(creds, f)
                self.logger.info('Gmail token saved')

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info('Gmail API authenticated')

    def _check_rate_limit(self) -> tuple:
        """
        Check if we're within rate limits.

        Returns:
            tuple: (allowed: bool, reason: str)
        """
        now = datetime.now()

        # Check cooldown
        if self.last_send_time:
            time_since_last = (now - self.last_send_time).total_seconds()
            if time_since_last < self.cooldown_seconds:
                return False, f'Cooldown period ({self.cooldown_seconds}s) not elapsed'

        # Check hourly limit
        one_hour_ago = now - timedelta(hours=1)
        sends_last_hour = sum(
            1 for entry in self.send_log
            if datetime.fromisoformat(entry['timestamp']) > one_hour_ago
            and entry.get('action') == 'send_email'
            and entry.get('result') == 'success'
        )

        if sends_last_hour >= self.max_per_hour:
            return False, f'Hourly limit reached ({sends_last_hour}/{self.max_per_hour})'

        # Check daily limit
        one_day_ago = now - timedelta(hours=24)
        sends_last_day = sum(
            1 for entry in self.send_log
            if datetime.fromisoformat(entry['timestamp']) > one_day_ago
            and entry.get('action') == 'send_email'
            and entry.get('result') == 'success'
        )

        if sends_last_day >= self.max_per_day:
            return False, f'Daily limit reached ({sends_last_day}/{self.max_per_day})'

        return True, 'OK'

    def _validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _create_message(self, to: str, subject: str, body: str,
                       attachment_path: str = None) -> dict:
        """Create email message."""
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # Add body
        message.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_path and Path(attachment_path).exists():
            filepath = Path(attachment_path)
            with open(filepath, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filepath.name}"'
                )
                message.attach(part)

        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}

    def send_email(self, to: str, subject: str, body: str,
                  attachment_path: str = None) -> dict:
        """
        Send an email.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            attachment_path: Optional path to attachment

        Returns:
            dict: Result with success status
        """
        # Validate email
        if not self._validate_email(to):
            return {
                'success': False,
                'error': f'Invalid email address: {to}'
            }

        # Check rate limit
        allowed, reason = self._check_rate_limit()
        if not allowed:
            return {
                'success': False,
                'error': f'Rate limit exceeded: {reason}'
            }

        # Dry run check
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would send email to {to}: {subject}')
            return {
                'success': True,
                'dry_run': True,
                'message': f'Email would be sent to {to}'
            }

        try:
            # Create and send message
            message = self._create_message(to, subject, body, attachment_path)
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            # Update rate limiting
            self.last_send_time = datetime.now()

            # Log the action
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'send_email',
                'to': to,
                'subject': subject,
                'message_id': sent_message.get('id', ''),
                'result': 'success'
            }
            self.send_log.append(log_entry)
            self._save_send_log(log_entry)

            self.logger.info(f'Email sent to {to}: {subject}')
            return {
                'success': True,
                'message_id': sent_message.get('id', ''),
                'sent_at': datetime.now().isoformat()
            }

        except HttpError as error:
            error_msg = str(error)
            self.logger.error(f'Error sending email: {error_msg}')
            return {
                'success': False,
                'error': error_msg
            }

    def create_draft(self, to: str, subject: str, body: str,
                    attachment_path: str = None) -> dict:
        """
        Create an email draft.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            attachment_path: Optional attachment path

        Returns:
            dict: Draft creation result
        """
        if not self._validate_email(to):
            return {
                'success': False,
                'error': f'Invalid email address: {to}'
            }

        try:
            message = self._create_message(to, subject, body, attachment_path)
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()

            self.logger.info(f'Draft created for {to}: {subject}')
            return {
                'success': True,
                'draft_id': draft.get('id', ''),
                'message': 'Draft created successfully'
            }

        except HttpError as error:
            self.logger.error(f'Error creating draft: {error}')
            return {
                'success': False,
                'error': str(error)
            }

    def list_recent_emails(self, limit: int = 10, days: int = 7) -> dict:
        """
        List recently sent emails.

        Args:
            limit: Number of emails to return
            days: Look back this many days

        Returns:
            dict: List of recent emails
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='in:sent',
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                details = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['To', 'Subject', 'Date']
                ).execute()

                headers = {
                    h['name']: h['value']
                    for h in details['payload'].get('headers', [])
                }

                emails.append({
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', ''),
                    'sent_at': headers.get('Date', '')
                })

            return {
                'success': True,
                'emails': emails,
                'count': len(emails)
            }

        except HttpError as error:
            self.logger.error(f'Error listing emails: {error}')
            return {
                'success': False,
                'error': str(error)
            }


def main():
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--credentials', type=str, default='./credentials.json',
                        help='Path to Gmail credentials JSON')
    parser.add_argument('--token', type=str, default=None,
                        help='Path to token file')
    parser.add_argument('--vault', type=str, default='./AI_Employee_Vault',
                        help='Path to vault for logging')
    parser.add_argument('--dry-run', action='store_true',
                        help='Don\'t actually send emails')
    parser.add_argument('--max-per-hour', type=int, default=10,
                        help='Max emails per hour')
    parser.add_argument('--max-per-day', type=int, default=50,
                        help='Max emails per day')
    parser.add_argument('--cooldown', type=int, default=30,
                        help='Cooldown between sends (seconds)')
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        server = EmailMCPServer(
            credentials_path=args.credentials,
            token_path=args.token,
            vault_path=args.vault,
            dry_run=args.dry_run,
            max_per_hour=args.max_per_hour,
            max_per_day=args.max_per_day,
            cooldown_seconds=args.cooldown
        )

        # Interactive mode
        print('\n' + '='*60)
        print('Email MCP Server - Ready to send emails!')
        print('='*60)
        print('\nCommands:')
        print('  send <to> <subject> <body>')
        print('  draft <to> <subject> <body>')
        print('  list [limit]')
        print('  quit')
        print('\n')

        while True:
            try:
                cmd = input('email> ').strip()
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd.startswith('send '):
                    parts = cmd.split(' ', 3)
                    if len(parts) >= 4:
                        result = server.send_email(parts[1], parts[2], parts[3])
                        print(json.dumps(result, indent=2))
                    else:
                        print('Usage: send <to@email.com> <Subject> <Body>')
                elif cmd.startswith('draft '):
                    parts = cmd.split(' ', 3)
                    if len(parts) >= 4:
                        result = server.create_draft(parts[1], parts[2], parts[3])
                        print(json.dumps(result, indent=2))
                    else:
                        print('Usage: draft <to@email.com> <Subject> <Body>')
                elif cmd.startswith('list'):
                    parts = cmd.split()
                    limit = int(parts[1]) if len(parts) > 1 else 10
                    result = server.list_recent_emails(limit)
                    print(json.dumps(result, indent=2))
                else:
                    print('Unknown command. Use: send, draft, list, or quit')

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f'Error: {e}')

    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
