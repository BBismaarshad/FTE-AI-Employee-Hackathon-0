"""
LinkedIn Authentication Helper

Provides authentication utilities for LinkedIn automation using Playwright.
Handles login, session persistence, and session validation.

Usage:
    # Interactive login (first time)
    python skills/linkedin_auth.py --login

    # Check if session is valid
    python skills/linkedin_auth.py --check

    # Clear saved session
    python skills/linkedin_auth.py --clear
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInAuth')

# Default session path
DEFAULT_SESSION_PATH = Path(__file__).parent.parent / 'credentials' / 'linkedin_session'


class LinkedInAuth:
    """Handles LinkedIn authentication and session management."""

    def __init__(self, session_path: str = None):
        self.session_path = Path(session_path) if session_path else DEFAULT_SESSION_PATH
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.context = None
        self.page = None

    def has_valid_session(self) -> bool:
        """
        Check if we have a valid LinkedIn session.

        Returns:
            bool: True if session exists and appears valid
        """
        if not self.session_path.exists():
            logger.info('No saved LinkedIn session found')
            return False

        # Check if session folder has meaningful content
        # Chrome stores cookies at Default/Network/Cookies
        cookies_file = self.session_path / 'Default' / 'Network' / 'Cookies'
        if cookies_file.exists():
            logger.info('Found saved LinkedIn session')
            return True

        # Also check alternative path
        cookies_file_alt = self.session_path / 'Default' / 'Cookies'
        if cookies_file_alt.exists():
            logger.info('Found saved LinkedIn session')
            return True

        # Check if Default folder exists with substantial content
        default_folder = self.session_path / 'Default'
        if default_folder.exists():
            # Check for key session files
            session_indicators = ['Local State', 'Last Browser', 'Network']
            if any((default_folder / f).exists() for f in session_indicators):
                logger.info('Found saved LinkedIn session')
                return True

        logger.info('LinkedIn session folder exists but appears empty')
        return False

    def login(self, headless: bool = False) -> bool:
        """
        Perform interactive LinkedIn login.

        Args:
            headless: Run browser without UI (not recommended for first login)

        Returns:
            bool: True if login succeeded
        """
        logger.info('Starting LinkedIn authentication...')
        logger.info('Browser will open - please login manually')

        try:
            self.playwright = sync_playwright().start()

            # Launch browser with persistent context
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=headless,
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            # Navigate to LinkedIn
            logger.info('Opening LinkedIn login page...')
            self.page.goto('https://www.linkedin.com/login', timeout=60000)

            # Wait for user to login
            logger.info('')
            logger.info('=' * 60)
            logger.info('Please login to LinkedIn in the browser window')
            logger.info('- Enter your email and password')
            logger.info('- Complete any 2FA or captcha if prompted')
            logger.info('- Wait until you see your LinkedIn feed')
            logger.info('- The session will be saved automatically')
            logger.info('=' * 60)
            logger.info('')

            # Wait for successful login (redirect to feed)
            try:
                # Wait up to 5 minutes for login
                self.page.wait_for_url('**/feed/**', timeout=300000)
                logger.info('✅ LinkedIn login detected!')

                # Give page time to fully load
                time.sleep(3)

                # Verify we're actually logged in
                if self._is_logged_in():
                    logger.info('✅ Authentication successful!')
                    logger.info(f'✅ Session saved to: {self.session_path}')
                    logger.info('')
                    logger.info('You can now use:')
                    logger.info('  - python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post')
                    logger.info('  - python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault')
                    return True
                else:
                    logger.error('❌ Login flow incomplete - please ensure you reached your feed')
                    return False

            except PlaywrightTimeout:
                logger.error('❌ Login timeout - please restart and try again')
                return False

        except Exception as e:
            logger.error(f'❌ Authentication error: {e}')
            return False

        finally:
            self._cleanup()

    def _is_logged_in(self) -> bool:
        """
        Verify we're logged in by checking for feed elements.

        Returns:
            bool: True if logged in
        """
        try:
            # Check current URL
            current_url = self.page.url
            if 'feed' in current_url or 'mynetwork' in current_url:
                return True

            # Check for feed elements
            feed_selectors = [
                '[data-view-name="feed-update"]',
                '.share-box-feed-entry__creator',
                '#feed-identity-module'
            ]

            for selector in feed_selectors:
                if self.page.query_selector(selector):
                    return True

            return False

        except Exception as e:
            logger.debug(f'Login check error: {e}')
            return False

    def clear_session(self):
        """Clear saved LinkedIn session."""
        if self.session_path.exists():
            import shutil
            shutil.rmtree(self.session_path)
            logger.info(f'✅ LinkedIn session cleared: {self.session_path}')
        else:
            logger.info('No session found to clear')

    def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.debug(f'Cleanup error: {e}')
        finally:
            self.context = None
            self.playwright = None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Authentication Helper')
    parser.add_argument('--login', action='store_true',
                        help='Perform interactive LinkedIn login')
    parser.add_argument('--check', action='store_true',
                        help='Check if LinkedIn session is valid')
    parser.add_argument('--clear', action='store_true',
                        help='Clear saved LinkedIn session')
    parser.add_argument('--session-path', type=str, default=None,
                        help='Path to store LinkedIn session')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode (not recommended for login)')
    args = parser.parse_args()

    auth = LinkedInAuth(session_path=args.session_path)

    if args.login:
        success = auth.login(headless=args.headless)
        sys.exit(0 if success else 1)

    elif args.check:
        if auth.has_valid_session():
            logger.info('✅ Valid LinkedIn session found')
            sys.exit(0)
        else:
            logger.info('❌ No valid LinkedIn session found')
            logger.info('Run with --login to authenticate')
            sys.exit(1)

    elif args.clear:
        auth.clear_session()
        sys.exit(0)

    else:
        # Default: show status
        logger.info('LinkedIn Authentication Helper')
        logger.info('')
        logger.info('Usage:')
        logger.info('  --login    Authenticate with LinkedIn (first time setup)')
        logger.info('  --check    Check if session is valid')
        logger.info('  --clear    Clear saved session')
        logger.info('')
        if auth.has_valid_session():
            logger.info('Status: ✅ Session saved and ready')
        else:
            logger.info('Status: ⚠️  No session found - run --login to authenticate')
        sys.exit(0)


if __name__ == '__main__':
    main()
