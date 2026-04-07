"""
LinkedIn Watcher - Monitors LinkedIn for messages, connection requests, and notifications.

This watcher:
1. Opens LinkedIn using Playwright (headless browser)
2. Scans for new messages, connection requests, and post notifications
3. Creates action files in Needs_Action folder for each new item
4. Tracks processed items to avoid duplicates

Usage:
    python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault

Credentials:
    First run will require LinkedIn login via browser.
    Session will be saved to credentials/linkedin_session/ folder.

Note:
    Automated LinkedIn access may violate Terms of Service.
    Use at your own risk. Consider official LinkedIn API for production.
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
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_watcher import BaseWatcher, setup_logging

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    raise ImportError(
        'Playwright is required for LinkedIn Watcher.\n'
        'Install with: pip install playwright\n'
        'Then run: playwright install chromium'
    )


class LinkedInWatcher(BaseWatcher):
    """Watches LinkedIn for messages, connections, and notifications."""

    def __init__(self, vault_path: str, session_path: str = None,
                 check_interval: int = 300, headless: bool = False,
                 timeout: int = 30000):
        super().__init__(vault_path, check_interval)

        # Session path for persistent login
        if session_path is None:
            session_path = str(Path(__file__).parent.parent / 'credentials' / 'linkedin_session')
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Browser settings
        self.headless = headless
        self.timeout = timeout

        # Track processed items (by hash)
        self.processed_ids = set()
        self._load_processed_ids()

        # Browser state
        self.playwright = None
        self.context = None
        self.page = None

        # Keywords to monitor in messages/notifications
        self.keywords = ['opportunity', 'project', 'collaboration', 'invoice', 
                        'payment', 'urgent', 'partnership', 'consulting']

    def _load_processed_ids(self):
        """Load list of already processed item IDs."""
        state_file = self.vault_path / '.state' / 'linkedin_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            try:
                self.processed_ids = set(state_file.read_text().splitlines())
                self.logger.info(f'Loaded {len(self.processed_ids)} processed LinkedIn items')
            except Exception as e:
                self.logger.warning(f'Error loading processed IDs: {e}')
                self.processed_ids = set()

    def _save_processed_ids(self):
        """Save list of processed item IDs."""
        state_file = self.vault_path / '.state' / 'linkedin_watcher.txt'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Keep only last 500 IDs
            ids_list = list(self.processed_ids)[-500:]
            state_file.write_text('\n'.join(ids_list))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')

    def _generate_item_id(self, item_type: str, content: str) -> str:
        """Generate a unique ID for an item to track duplicates."""
        today = datetime.now().strftime('%Y-%m-%d')
        hash_content = f'{item_type}:{content}:{today}'
        return hashlib.md5(hash_content.encode()).hexdigest()

    def _initialize_browser(self):
        """Initialize Playwright browser with LinkedIn session."""
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

    def _wait_for_linkedin_loaded(self) -> bool:
        """
        Wait for LinkedIn to load completely.

        Returns:
            bool: True if LinkedIn is loaded, False otherwise
        """
        try:
            self.logger.info('Waiting for LinkedIn to load...')

            # Navigate to LinkedIn messaging page
            self.page.goto('https://www.linkedin.com/messaging/', 
                          timeout=self.timeout, wait_until='networkidle')

            # Wait for page to load - check for login or feed
            if 'login' in self.page.url.lower():
                self.logger.warning(
                    'LinkedIn login required! Please login manually in the browser window.\n'
                    'Session will be saved for future runs.'
                )
                # Wait for user to login
                try:
                    self.page.wait_for_url('**/feed/**', timeout=120000)
                    self.logger.info('LinkedIn login detected!')
                except PlaywrightTimeout:
                    self.logger.error('Login timeout. Please restart the watcher.')
                    return False

            # Navigate back to messaging
            self.page.goto('https://www.linkedin.com/messaging/', 
                          timeout=10000, wait_until='networkidle')

            self.logger.info('LinkedIn loaded successfully')
            return True

        except Exception as e:
            self.logger.error(f'Error waiting for LinkedIn to load: {e}')
            return False

    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new messages and notifications.

        Returns:
            list: List of new items
        """
        items = []

        # Initialize browser if needed
        if not self.page:
            if not self._initialize_browser():
                return items

            if not self._wait_for_linkedin_loaded():
                return items

        try:
            # Check for new messages
            messages = self._check_messages()
            items.extend(messages)

            # Check for notifications
            notifications = self._check_notifications()
            items.extend(notifications)

            self.logger.info(f'Found {len(items)} new LinkedIn items')
            return items

        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            # Try to recover by reinitializing
            self._cleanup_browser()
            return []

    def _check_messages(self) -> list:
        """Check LinkedIn messaging for new conversations."""
        messages = []

        try:
            # Navigate to messaging
            self.page.goto('https://www.linkedin.com/messaging/', 
                          timeout=10000, wait_until='networkidle')
            time.sleep(2)

            # Look for messaging threads
            # LinkedIn uses various selectors for message threads
            thread_selectors = [
                'ul.msg-conversations-list > li',
                '[data-view-name="conversation-card"]',
                '.msg-conversation-card'
            ]

            threads_found = False
            for selector in thread_selectors:
                threads = self.page.query_selector_all(selector)
                if threads:
                    threads_found = True
                    self.logger.info(f'Found {len(threads)} message threads')

                    for thread in threads[:10]:  # Limit to 10 most recent
                        try:
                            # Extract sender name
                            name_elem = thread.query_selector(
                                '.msg-conversation-card__actor-name, '
                                '[data-view-name="conversation-card-actor-name"] a'
                            )
                            sender_name = name_elem.inner_text().strip() if name_elem else 'Unknown'

                            # Extract last message preview
                            message_elem = thread.query_selector(
                                '.msg-conversation-card__message-line, '
                                '.msg-conversation-card__last-message'
                            )
                            message_text = message_elem.inner_text().strip() if message_elem else ''

                            # Check if there's an unread indicator
                            has_unread = thread.query_selector(
                                '.msg-conversation-card__unread-count, '
                                '[aria-label*="unread"]'
                            ) is not None

                            # Only process if has unread or contains keywords
                            if has_unread or any(kw in message_text.lower() 
                                               for kw in self.keywords):
                                item_id = self._generate_item_id(
                                    'message', f'{sender_name}:{message_text}'
                                )

                                if item_id not in self.processed_ids:
                                    messages.append({
                                        'id': item_id,
                                        'type': 'linkedin_message',
                                        'from': sender_name,
                                        'text': message_text,
                                        'has_unread': has_unread,
                                        'matched_keywords': [
                                            kw for kw in self.keywords
                                            if kw in message_text.lower()
                                        ],
                                        'url': 'https://www.linkedin.com/messaging/',
                                        'timestamp': datetime.now().isoformat()
                                    })

                        except Exception as e:
                            self.logger.debug(f'Error processing message thread: {e}')
                            continue

                    break

            if not threads_found:
                self.logger.debug('No message threads found - may need login')

        except Exception as e:
            self.logger.error(f'Error checking messages: {e}')

        return messages

    def _check_notifications(self) -> list:
        """Check LinkedIn notifications for new items."""
        notifications = []

        try:
            # Navigate to notifications page
            self.page.goto('https://www.linkedin.com/notifications/', 
                          timeout=10000, wait_until='networkidle')
            time.sleep(2)

            # Look for notification items
            notification_selectors = [
                '.notification-card',
                '[data-view-name="notification-card"]',
                '.scaffold-layout__list > li'
            ]

            for selector in notification_selectors:
                notif_elements = self.page.query_selector_all(selector)
                if notif_elements:
                    self.logger.info(f'Found {len(notif_elements)} notifications')

                    for notif in notif_elements[:10]:  # Limit to 10 most recent
                        try:
                            # Extract notification text
                            text_elem = notif.query_selector(
                                '.notification-card__main-content-text, '
                                '.notification-card__summary-text, '
                                'span a span'
                            )
                            notif_text = text_elem.inner_text().strip() if text_elem else ''

                            # Determine notification type
                            notif_type = 'general'
                            if any(kw in notif_text.lower() 
                                  for kw in ['connected', 'accepted', 'invitation']):
                                notif_type = 'connection'
                            elif any(kw in notif_text.lower() 
                                    for kw in ['viewed', 'comment', 'like', 'reaction']):
                                notif_type = 'engagement'
                            elif any(kw in notif_text.lower() 
                                    for kw in ['job', 'position', 'opportunity']):
                                notif_type = 'opportunity'

                            # Only process important notification types
                            if notif_type in ['connection', 'opportunity']:
                                item_id = self._generate_item_id(
                                    f'notification_{notif_type}', notif_text
                                )

                                if item_id not in self.processed_ids:
                                    notifications.append({
                                        'id': item_id,
                                        'type': f'linkedin_notification_{notif_type}',
                                        'text': notif_text[:200],
                                        'category': notif_type,
                                        'url': 'https://www.linkedin.com/notifications/',
                                        'timestamp': datetime.now().isoformat()
                                    })

                        except Exception as e:
                            self.logger.debug(f'Error processing notification: {e}')
                            continue

                    break

        except Exception as e:
            self.logger.error(f'Error checking notifications: {e}')

        return notifications

    def create_action_file(self, item: dict) -> Path:
        """
        Create action file for a LinkedIn item.

        Args:
            item: Item dict with type, text, timestamp, etc.

        Returns:
            Path: Path to the created action file
        """
        # Sanitize sender name for filename
        from_name = item.get('from', 'LinkedIn')
        safe_from = ''.join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in from_name
        )[:30]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_filename = f'LINKEDIN_{item["type"]}_{safe_from}_{timestamp}.md'
        action_path = self.needs_action / action_filename

        # Determine priority
        priority = 'normal'
        if item.get('has_unread') or item.get('category') == 'opportunity':
            priority = 'high'

        content = f"""---
type: {item['type']}
from: {from_name}
received: {item['timestamp']}
priority: {priority}
linkedin_url: {item.get('url', '')}
status: pending
---

# LinkedIn {'Message' if 'message' in item['type'] else 'Notification'}

## Metadata
- **Type**: {item['type']}
- **From**: {from_name}
- **Received**: {item['timestamp']}
- **Priority**: {priority}
- **LinkedIn URL**: {item.get('url', '')}

"""
        if 'message' in item['type']:
            content += f"""## Message Content
{item.get('text', '')}

## Matched Keywords
{', '.join(item.get('matched_keywords', []))}

## Suggested Actions
- [ ] Read full conversation on LinkedIn
- [ ] Respond to message
- [ ] Check if action required
- [ ] Archive after processing

"""
        else:
            content += f"""## Notification Content
{item.get('text', '')}

## Category
{item.get('category', 'general')}

## Suggested Actions
- [ ] Review notification on LinkedIn
- [ ] Take appropriate action if needed
- [ ] Archive after processing

"""

        content += f"""---
*Detected by LinkedIn Watcher at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        action_path.write_text(content, encoding='utf-8')

        # Mark as processed
        self.processed_ids.add(item['id'])
        self._save_processed_ids()

        self.logger.info(f'Created action file: {action_filename}')
        return action_path

    def run_once(self) -> int:
        """
        Run a single check cycle with proper cleanup.

        Returns:
            int: Number of action files created
        """
        try:
            items = self.check_for_updates()
            count = 0
            for item in items:
                filepath = self.create_action_file(item)
                self.logger.info(f'Created action file: {filepath}')
                count += 1
            return count
        except Exception as e:
            self.logger.error(f'Error in LinkedIn watcher: {e}', exc_info=True)
            return 0
        finally:
            # Clean up browser after each run to prevent resource leaks
            self._cleanup_browser()

    def run(self):
        """Main watcher loop - continuously monitor LinkedIn."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}', exc_info=True)
            finally:
                # Clean up and recreate browser for next iteration
                self._cleanup_browser()

            time.sleep(self.check_interval)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--session-path', type=str, default=None,
                        help='Path to store LinkedIn browser session')
    parser.add_argument('--interval', type=int, default=300,
                        help='Check interval in seconds (default: 300 = 5 min)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for testing/scheduled tasks)')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Browser timeout in milliseconds (default: 30000)')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('LinkedInWatcher')

    try:
        # Create watcher
        watcher = LinkedInWatcher(
            vault_path=args.vault,
            session_path=args.session_path,
            check_interval=args.interval,
            headless=args.headless,
            timeout=args.timeout
        )

        if args.once:
            # Run single check
            count = watcher.run_once()
            logger.info(f'LinkedIn watcher created {count} action files')
        else:
            # Run continuously
            logger.info(f'Monitoring LinkedIn for messages and notifications')
            logger.info(f'Vault: {args.vault}')
            logger.info(f'Interval: {args.interval}s')
            try:
                watcher.run()
            except KeyboardInterrupt:
                logger.info('LinkedIn watcher stopped by user')

    except ImportError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
