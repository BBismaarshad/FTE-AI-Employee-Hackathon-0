"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages with keywords.

This watcher:
1. Opens WhatsApp Web using Playwright (headless browser)
2. Scans for unread messages containing urgent keywords
3. Creates action files in Needs_Action folder
4. Tracks processed messages to avoid duplicates

Usage:
    python whatsapp_watcher.py --vault /path/to/vault

Security Note:
    WhatsApp Web session is stored locally - protect this data!
    Be aware of WhatsApp's Terms of Service regarding automation.

Warning:
    This uses web automation which may violate WhatsApp's ToS.
    Use at your own risk. Consider using WhatsApp Business API for production.
"""

import os
import sys
import time
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher, setup_logging

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    raise ImportError(
        'Playwright is required for WhatsApp Watcher.\n'
        'Install with: pip install playwright\n'
        'Then run: playwright install chromium'
    )


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for messages with important keywords."""

    def __init__(self, vault_path: str, session_path: str = None,
                 keywords: list = None, check_interval: int = 30,
                 headless: bool = False, timeout: int = 30000):
        super().__init__(vault_path, check_interval)

        # Session path for persistent login
        if session_path is None:
            session_path = str(Path(__file__).parent.parent / 'credentials' / 'whatsapp_session')
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Keywords to monitor
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help']
        self.keywords = [kw.lower() for kw in self.keywords]

        # Browser settings
        self.headless = headless
        self.timeout = timeout

        # Track processed messages (by hash of chat_id + message text + timestamp)
        self.processed_ids = set()
        self._load_processed_ids()

        # Browser state
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _load_processed_ids(self):
        """Load list of already processed message IDs."""
        state_file = self.vault_path / '.state' / 'whatsapp_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            try:
                self.processed_ids = set(state_file.read_text().splitlines())
                self.logger.info(f'Loaded {len(self.processed_ids)} processed message IDs')
            except Exception as e:
                self.logger.warning(f'Error loading processed IDs: {e}')
                self.processed_ids = set()

    def _save_processed_ids(self):
        """Save list of processed message IDs."""
        state_file = self.vault_path / '.state' / 'whatsapp_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Keep only last 500 IDs
            ids_list = list(self.processed_ids)[-500:]
            state_file.write_text('\n'.join(ids_list))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')

    def _generate_message_id(self, chat_name: str, message_text: str, timestamp: str) -> str:
        """Generate a unique ID for a message to track duplicates."""
        content = f'{chat_name}:{message_text}:{timestamp}'
        return hashlib.md5(content.encode()).hexdigest()

    def _initialize_browser(self):
        """Initialize Playwright browser with WhatsApp Web session."""
        try:
            self.playwright = sync_playwright().start()

            # Launch browser with persistent context for session
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                viewport={'width': 1280, 'height': 720}
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            self.logger.info('Browser initialized successfully')
            return True

        except Exception as e:
            self.logger.error(f'Error initializing browser: {e}')
            self._cleanup_browser()
            return False

    def _cleanup_browser(self):
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.logger.debug(f'Error cleaning up browser: {e}')
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None

    def _wait_for_whatsapp_loaded(self) -> bool:
        """
        Wait for WhatsApp Web to load completely.

        Returns:
            bool: True if WhatsApp Web is loaded, False otherwise
        """
        try:
            self.logger.info('Waiting for WhatsApp Web to load...')

            # Navigate to WhatsApp Web if not already there
            if 'web.whatsapp.com' not in self.page.url:
                self.page.goto('https://web.whatsapp.com', timeout=self.timeout)

            # Wait for either QR code (not logged in) or chat list (logged in)
            try:
                # Check if we need to scan QR code
                qr_selector = 'canvas[aria-label="Scan me!"]'
                self.page.wait_for_selector(qr_selector, timeout=5000)
                self.logger.warning(
                    'QR code detected! Please scan with your phone to authenticate.\n'
                    'Session will be saved for future runs.'
                )
                # Wait for user to scan and login
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                self.logger.info('WhatsApp Web login successful!')

            except PlaywrightTimeout:
                # QR code not found - might already be logged in
                pass

            # Wait for chat list to load (indicates successful login)
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
            self.logger.info('WhatsApp Web loaded successfully')
            return True

        except PlaywrightTimeout:
            self.logger.error('Timeout waiting for WhatsApp Web to load')
            return False
        except Exception as e:
            self.logger.error(f'Error waiting for WhatsApp to load: {e}')
            return False

    def check_for_updates(self) -> list:
        """
        Check WhatsApp for unread messages with keywords.

        Returns:
            list: List of messages containing keywords
        """
        messages = []

        # Initialize browser if needed
        if not self.page:
            if not self._initialize_browser():
                return messages

            if not self._wait_for_whatsapp_loaded():
                return messages

        try:
            # Get all chats with unread messages
            # This selector looks for unread message indicators
            unread_indicators = self.page.query_selector_all('[aria-label*="unread"]')

            self.logger.info(f'Found {len(unread_indicators)} chats with unread messages')

            for indicator in unread_indicators:
                try:
                    # Click on the chat to view messages
                    indicator.click()
                    time.sleep(1)  # Wait for messages to load

                    # Get chat name
                    chat_name_selector = 'span[title]'
                    chat_element = self.page.query_selector(chat_name_selector)
                    chat_name = chat_element.get_attribute('title') if chat_element else 'Unknown'

                    # Get message text elements
                    message_elements = self.page.query_selector_all(
                        'div[data-testid="chat-body-content"] span[dir="auto"]'
                    )

                    for msg_elem in message_elements:
                        message_text = msg_elem.inner_text().strip()

                        # Check if message contains keywords
                        matched_keywords = [
                            kw for kw in self.keywords
                            if kw in message_text.lower()
                        ]

                        if matched_keywords:
                            # Generate unique ID
                            msg_id = self._generate_message_id(
                                chat_name, message_text, datetime.now().strftime('%Y-%m-%d')
                            )

                            # Skip if already processed
                            if msg_id not in self.processed_ids:
                                messages.append({
                                    'id': msg_id,
                                    'chat_name': chat_name,
                                    'message_text': message_text,
                                    'matched_keywords': matched_keywords,
                                    'timestamp': datetime.now().isoformat()
                                })

                except Exception as e:
                    self.logger.debug(f'Error processing chat: {e}')
                    continue

            self.logger.info(f'Found {len(messages)} new messages with keywords')
            return messages

        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            # Try to recover by reinitializing
            self._cleanup_browser()
            return []

    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for a WhatsApp message.

        Args:
            message: Message dict with chat_name, message_text, matched_keywords

        Returns:
            Path: Path to the created action file
        """
        # Sanitize chat name for filename
        safe_chat_name = ''.join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in message['chat_name']
        )[:30]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_filename = f'WHATSAPP_{safe_chat_name}_{timestamp}.md'
        action_path = self.needs_action / action_filename

        # Determine priority based on keyword urgency
        high_priority_keywords = ['urgent', 'asap', 'immediately', 'emergency']
        priority = 'high' if any(
            kw in high_priority_keywords for kw in message['matched_keywords']
        ) else 'normal'

        content = f"""---
type: whatsapp_message
from: {message['chat_name']}
chat_id: {message['chat_name']}
received: {message['timestamp']}
priority: {priority}
matched_keywords: {', '.join(message['matched_keywords'])}
status: pending
---

# WhatsApp Message from {message['chat_name']}

## Metadata
- **From**: {message['chat_name']}
- **Received**: {message['timestamp']}
- **Priority**: {priority}
- **Matched Keywords**: {', '.join(message['matched_keywords'])}

## Message Content
{message['message_text']}

## Suggested Actions
- [ ] Read full conversation in WhatsApp
- [ ] Respond to contact
- [ ] Take requested action
- [ ] Follow up if needed
- [ ] Archive after processing

---
*Detected by WhatsApp Watcher at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        action_path.write_text(content)

        # Mark as processed
        self.processed_ids.add(message['id'])
        self._save_processed_ids()

        self.logger.info(
            f'Created action file: {action_filename} '
            f'(keywords: {", ".join(message["matched_keywords"])})'
        )
        return action_path

    def run_once(self) -> int:
        """
        Run a single check cycle with proper cleanup.

        Returns:
            int: Number of action files created
        """
        try:
            messages = self.check_for_updates()
            count = 0
            for message in messages:
                filepath = self.create_action_file(message)
                self.logger.info(f'Created action file: {filepath}')
                count += 1
            return count
        except Exception as e:
            self.logger.error(f'Error in WhatsApp watcher: {e}', exc_info=True)
            return 0
        finally:
            # Clean up browser after each run to prevent resource leaks
            self._cleanup_browser()

    def run(self):
        """Main watcher loop - continuously monitor WhatsApp Web."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                messages = self.check_for_updates()
                for message in messages:
                    filepath = self.create_action_file(message)
                    self.logger.info(f'Created action file: {filepath}')
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}', exc_info=True)
            finally:
                # Clean up and recreate browser for next iteration
                self._cleanup_browser()

            time.sleep(self.check_interval)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--session-path', type=str, default=None,
                        help='Path to store WhatsApp session data')
    parser.add_argument('--keywords', type=str, nargs='+',
                        default=['urgent', 'asap', 'invoice', 'payment', 'help'],
                        help='Keywords to monitor (default: urgent asap invoice payment help)')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for testing/scheduled tasks)')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Browser timeout in milliseconds (default: 30000)')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('WhatsAppWatcher')

    try:
        # Create watcher
        watcher = WhatsAppWatcher(
            vault_path=args.vault,
            session_path=args.session_path,
            keywords=args.keywords,
            check_interval=args.interval,
            headless=args.headless,
            timeout=args.timeout
        )

        if args.once:
            # Run single check
            count = watcher.run_once()
            logger.info(f'WhatsApp watcher created {count} action files')
        else:
            # Run continuously
            logger.info(f'Monitoring WhatsApp Web for keyword messages')
            logger.info(f'Vault: {args.vault}')
            logger.info(f'Keywords: {", ".join(args.keywords)}')
            logger.info(f'Interval: {args.interval}s')
            try:
                watcher.run()
            except KeyboardInterrupt:
                logger.info('WhatsApp watcher stopped by user')

    except ImportError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
