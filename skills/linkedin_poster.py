"""
LinkedIn Auto-Poster - Generate and post business content to LinkedIn.

This skill:
1. Generates professional LinkedIn posts about your business
2. Creates draft files for human review
3. Posts approved content using Playwright automation
4. Tracks posts and engagement in logs

Usage:
    # Generate a draft for review
    python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate

    # Generate with approval workflow
    python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post

    # Post approved content (called by orchestrator)
    python skills/linkedin_poster.py --vault ./AI_Employee_Vault --execute-approved

    # First-time LinkedIn authentication
    python skills/linkedin_auth.py --login

Security Note:
    Automated posting may violate LinkedIn's Terms of Service.
    Use with caution and consider official LinkedIn API for production.
    Always review AI-generated content before publishing.
"""

import os
import sys
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import setup_logging
from skills.linkedin_auth import LinkedInAuth

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    raise ImportError(
        'Playwright is required for LinkedIn posting.\n'
        'Install with: pip install playwright\n'
        'Then run: playwright install chromium'
    )


class LinkedInPoster:
    """Generates and posts LinkedIn content for business promotion."""

    # Content templates for different categories
    TEMPLATES = {
        'service_announcement': [
            {
                'text': """🚀 Excited to announce our new {service} service!

We help businesses {benefit} with cutting-edge {technology} solutions.

👉 {call_to_action}

{hashtags}""",
                'hashtags': ['#BusinessGrowth', '#Innovation', '#TechSolutions']
            },
            {
                'text': """📢 New Service Alert!

Introducing {service} - designed to help you {benefit}.

Why choose us?
✅ {feature_1}
✅ {feature_2}
✅ {feature_3}

{call_to_action}

{hashtags}""",
                'hashtags': ['#NewService', '#BusinessEfficiency', '#Professional']
            }
        ],
        'success_story': [
            {
                'text': """📊 Client Success Story:

A {industry} business was {pain_point}.

We implemented a solution that:
✅ {result_1}
✅ {result_2}
✅ {result_3}

The result? {impact}

Ready to transform your operations? Let's talk!

{hashtags}""",
                'hashtags': ['#CaseStudy', '#Results', '#BusinessGrowth']
            },
            {
                'text': """💼 Success Story of the Week:

Client Challenge: {challenge}

Our Solution: {solution}

Results After {timeframe}:
📈 {metric_1}
📈 {metric_2}
📈 {metric_3}

This is the power of smart automation!

{hashtags}""",
                'hashtags': ['#ClientSuccess', '#Transformation', '#Success']
            }
        ],
        'industry_insight': [
            {
                'text': """💡 Quick Tip for Business Owners:

Did you know? {statistic}

Top {number} things to {action}:
1️⃣ {tip_1}
2️⃣ {tip_2}
3️⃣ {tip_3}

{engagement_question}

{hashtags}""",
                'hashtags': ['#BusinessTips', '#Productivity', '#Insights']
            },
            {
                'text': """🎯 Industry Insight:

{insight_statement}

Here's what this means for your business:

{explanation}

{call_to_action}

{hashtags}""",
                'hashtags': ['#IndustryInsights', '#BusinessStrategy', '#Leadership']
            }
        ],
        'behind_the_scenes': [
            {
                'text': """🔧 Behind the Scenes:

{activity_description}

{personal_reflection}

{hashtags}""",
                'hashtags': ['#TechLife', '#Building', '#Innovation']
            },
            {
                'text': """💻 What We're Working On:

{project_description}

{value_proposition}

{hashtags}""",
                'hashtags': ['#WorkInProgress', '#Innovation', '#Technology']
            }
        ],
        'thought_leadership': [
            {
                'text': """🤔 Hot Take: {controversial_statement}

Here's why I believe this:

{reasoning}

{engagement_question}

{hashtags}""",
                'hashtags': ['#ThoughtLeadership', '#FutureOfWork', '#Innovation']
            }
        ]
    }

    def __init__(self, vault_path: str, session_path: str = None,
                 headless: bool = False):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else \
            self.vault_path.parent / 'credentials' / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless

        # Authentication helper
        self.auth = LinkedInAuth(session_path=str(self.session_path))

        # Setup folders
        self.drafts_folder = self.vault_path / 'Drafts' / 'LinkedIn'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)

        self.pending_approval = self.vault_path / 'Pending_Approval' / 'LinkedIn'
        self.pending_approval.mkdir(parents=True, exist_ok=True)

        self.approved_folder = self.vault_path / 'Approved' / 'LinkedIn'
        self.approved_folder.mkdir(parents=True, exist_ok=True)

        self.rejected_folder = self.vault_path / 'Rejected' / 'LinkedIn'
        self.rejected_folder.mkdir(parents=True, exist_ok=True)

        self.done_folder = self.vault_path / 'Done' / 'LinkedIn'
        self.done_folder.mkdir(parents=True, exist_ok=True)

        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('LinkedInPoster')

        # Load business goals
        self.business_goals = self._load_business_goals()

    def _load_business_goals(self) -> dict:
        """Load business goals to guide content generation."""
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            content = goals_file.read_text()
            # Simple parsing - in production, use proper YAML parser
            goals = {
                'services': [],
                'campaigns': [],
                'key_messages': []
            }

            # Extract services
            if 'Active Projects' in content or 'services' in content.lower():
                # Look for bullet points under relevant sections
                lines = content.split('\n')
                in_section = False
                for line in lines:
                    if any(kw in line.lower() for kw in ['project', 'service', 'campaign']):
                        in_section = True
                        continue
                    if in_section and line.strip().startswith('-'):
                        goals['services'].append(line.strip('- '))
                    elif in_section and line.startswith('#'):
                        in_section = False

            return goals

        return {
            'services': ['AI Automation Consulting'],
            'campaigns': [],
            'key_messages': ['Transform your business with AI']
        }

    def generate_post(self, category: str = None) -> dict:
        """
        Generate a LinkedIn post draft.

        Args:
            category: Post category (random if None)

        Returns:
            dict: Post content with metadata
        """
        # Select category
        if category is None:
            category = random.choice(list(self.TEMPLATES.keys()))

        templates = self.TEMPLATES.get(category, self.TEMPLATES['industry_insight'])
        template = random.choice(templates)

        # Generate content based on template
        post_data = self._fill_template(template, category)

        return post_data

    def _fill_template(self, template: dict, category: str) -> dict:
        """Fill template with actual content."""
        text = template['text']
        hashtags = template['hashtags']

        # Fill based on category
        if category == 'service_announcement':
            services = self.business_goals.get('services', ['AI Solutions'])
            service = services[0] if services else 'AI Automation'

            text = text.replace('{service}', service)
            text = text.replace('{benefit}', 'save 20+ hours per week')
            text = text.replace('{technology}', 'AI and automation')
            text = text.replace('{call_to_action}', 'DM me to learn how we can transform your workflow.')
            text = text.replace('{feature_1}', 'Reduce manual work by 85%')
            text = text.replace('{feature_2}', 'Cut errors by 95%')
            text = text.replace('{feature_3}', 'Save thousands in operational costs')

        elif category == 'success_story':
            text = text.replace('{industry}', 'local')
            text = text.replace('{pain_point}', 'spending 15 hours/week on manual data entry')
            text = text.replace('{result_1}', 'Reduced processing time by 85%')
            text = text.replace('{result_2}', 'Cut errors by 95%')
            text = text.replace('{result_3}', 'Saved $3,000/month in labor costs')
            text = text.replace('{impact}', 'They can now focus on growing their business instead of managing spreadsheets.')
            text = text.replace('{challenge}', 'Manual processes consuming valuable time')
            text = text.replace('{solution}', 'AI-powered automation system')
            text = text.replace('{timeframe}', '30 days')
            text = text.replace('{metric_1}', 'Processing time: -85%')
            text = text.replace('{metric_2}', 'Error rate: -95%')
            text = text.replace('{metric_3}', 'Monthly savings: $3,000')

        elif category == 'industry_insight':
            text = text.replace('{statistic}', '80% of repetitive business tasks can be automated with existing AI tools.')
            text = text.replace('{number}', '3')
            text = text.replace('{action}', 'automate first')
            text = text.replace('{tip_1}', 'Email responses & scheduling')
            text = text.replace('{tip_2}', 'Invoice generation & tracking')
            text = text.replace('{tip_3}', 'Customer follow-ups')
            text = text.replace('{engagement_question}', "What's the one task you wish you could automate today?")
            text = text.replace('{insight_statement}', 'The future of business is automated workflows with human oversight.')
            text = text.replace('{explanation}', 'Companies that embrace automation while maintaining human quality control are seeing 3-5x productivity gains.')
            text = text.replace('{call_to_action}', 'Ready to future-proof your business?')

        elif category == 'behind_the_scenes':
            text = text.replace('{activity_description}',
                              'Working on an AI system that will help a client automatically process 500+ invoices per month!')
            text = text.replace('{personal_reflection}',
                              'Love solving real-world problems with technology. This is what innovation looks like! 💪')
            text = text.replace('{project_description}',
                              'Building an intelligent workflow system that learns and adapts over time.')
            text = text.replace('{value_proposition}',
                              'This will save our client 40+ hours per month of manual work.')

        elif category == 'thought_leadership':
            text = text.replace('{controversial_statement}',
                              'Most businesses don\'t need more people - they need better automation.')
            text = text.replace('{reasoning}',
                              'I\'ve seen companies hire 10 people for tasks that could be automated with 2 systems and 1 overseer.')
            text = text.replace('{engagement_question}',
                              'What\'s your take - hire more people or automate more processes?')

        # Add hashtags
        hashtag_str = ' '.join(hashtags)
        text = text.replace('{hashtags}', hashtag_str)

        return {
            'text': text.strip(),
            'category': category,
            'hashtags': hashtags,
            'generated_at': datetime.now().isoformat()
        }

    def create_draft_file(self, post_data: dict) -> Path:
        """
        Create a draft file for human review.

        Args:
            post_data: Generated post content

        Returns:
            Path: Path to the draft file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        draft_name = f"{timestamp}_{post_data['category']}.md"
        draft_path = self.drafts_folder / draft_name

        content = f"""---
type: linkedin_draft
category: {post_data['category']}
created: {post_data['generated_at']}
status: pending_review
hashtags: {' '.join(post_data['hashtags'])}
estimated_reach: professional
---

# LinkedIn Post Draft

## Content
{post_data['text']}

## Metadata
- **Category**: {post_data['category']}
- **Hashtags**: {' '.join(post_data['hashtags'])}
- **Generated At**: {post_data['generated_at']}
- **Status**: Pending Review

## Suggested Actions
- [ ] Review content for accuracy
- [ ] Edit tone if needed
- [ ] Move to Pending_Approval/LinkedIn/ when ready to post
- [ ] Approved posts will be published automatically

---
*Generated by AI Employee at {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        draft_path.write_text(content, encoding='utf-8')
        self.logger.info(f'Created draft: {draft_path.name}')
        return draft_path

    def create_approval_request(self, draft_path: Path) -> Path:
        """
        Create an approval request for a draft.

        Args:
            draft_path: Path to the draft file

        Returns:
            Path: Path to the approval request
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        approval_name = f"POST_{timestamp}_pending.md"
        approval_path = self.pending_approval / approval_name

        # Read draft content
        draft_content = draft_path.read_text(encoding='utf-8')

        content = f"""---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
status: pending
draft_file: {draft_path.name}
---

# LinkedIn Post - Approval Required

Ready to post this content to LinkedIn?

{draft_content}

## To Approve
Move this file to /Approved/LinkedIn/ folder.

## To Reject
Move this file to /Rejected/LinkedIn/ folder or delete.

---
*Approval required for LinkedIn posting at {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        approval_path.write_text(content, encoding='utf-8')
        self.logger.info(f'Created approval request: {approval_path.name}')
        return approval_path

    def post_to_linkedin(self, text: str) -> bool:
        """
        Post content to LinkedIn using Playwright.

        Args:
            text: Post text content

        Returns:
            bool: True if posting succeeded
        """
        try:
            # Check if we have a valid session
            if not self.auth.has_valid_session():
                self.logger.error('No valid LinkedIn session found')
                self.logger.error('Run: python skills/linkedin_auth.py --login')
                return False

            self.logger.info('Opening LinkedIn to publish post...')

            with sync_playwright() as p:
                # Launch browser with saved session
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                try:
                    page.goto('https://www.linkedin.com', timeout=60000, wait_until='domcontentloaded')
                    time.sleep(3)
                except Exception as nav_error:
                    self.logger.warning(f'Navigation with domcontentloaded failed: {nav_error}')
                    # Try with networkidle as fallback
                    try:
                        page.goto('https://www.linkedin.com', timeout=60000, wait_until='networkidle')
                        time.sleep(3)
                    except Exception as nav_error2:
                        self.logger.error(f'All navigation attempts failed: {nav_error2}')
                        context.close()
                        return False

                # Check if we're logged in
                if 'login' in page.url.lower():
                    self.logger.error('LinkedIn session expired or invalid')
                    self.logger.error('Please re-authenticate: python skills/linkedin_auth.py --login')
                    context.close()
                    return False

                self.logger.info('Successfully logged in to LinkedIn')
                
                # Copy text to clipboard
                self.logger.info('Copying post content to clipboard...')
                page.evaluate(f'navigator.clipboard.writeText({json.dumps(text)})')
                time.sleep(0.5)

                # Method 1: Try the new LinkedIn UI
                success = self._post_via_start_box(page, text)

                if not success:
                    # Method 2: Try alternative posting flow
                    self.logger.info('Trying alternative posting method...')
                    success = self._post_via_new_post_flow(page, text)

                if success:
                    self.logger.info('✅ LinkedIn post published successfully!')
                else:
                    self.logger.warning('⚠️  Post UI elements not found - LinkedIn may have changed their interface')
                    self.logger.warning('⚠️  The draft is saved - you can manually copy-paste from:')
                    self.logger.warning(f'⚠️  {self.drafts_folder}')

                context.close()
                return success

        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False

    def _post_via_start_box(self, page, text: str) -> bool:
        """Post using the start box method (primary)."""
        try:
            # Find and click the post creation box
            post_start_selectors = [
                '[data-testid="share-box-start-post-creation-button"]',
                '.share-box-feed-entry__trigger',
                '[aria-label="Create a post"]',
                '[aria-label="Start a post"]',
                'button:has-text("Start a post")',
                'button:has-text("Post")',
                '.share-box__trigger'
            ]

            post_start_clicked = False
            for selector in post_start_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        if element.is_visible():
                            element.click()
                            post_start_clicked = True
                            self.logger.info(f'Clicked post creation with selector: {selector}')
                            time.sleep(3)  # Wait longer for dialog to open
                            break
                    if post_start_clicked:
                        break
                except Exception as e:
                    self.logger.debug(f'Selector {selector} failed: {e}')
                    continue

            if not post_start_clicked:
                self.logger.debug('Post start button not found')
                return False

            # Wait for dialog to appear - LinkedIn needs more time
            self.logger.info('Waiting for post dialog to open...')
            time.sleep(5)  # Increased wait time for dialog animation

            # Wait specifically for the dialog/modal to appear
            dialog_appeared = False
            for attempt in range(10):  # Wait up to 10 seconds
                try:
                    # Check for dialog/modal presence
                    dialog = page.query_selector('div[role="dialog"], div.artdeco-modal')
                    if dialog and dialog.is_visible():
                        dialog_appeared = True
                        self.logger.info('Post dialog opened')
                        break
                except Exception:
                    pass
                time.sleep(1)

            if not dialog_appeared:
                self.logger.warning('Dialog did not appear, but will try to proceed')

            # Take screenshot for debugging
            import os
            screenshot_path = os.path.join(os.getcwd(), 'linkedin_debug_dialog.png')
            page.screenshot(path=screenshot_path)
            self.logger.info(f'Took screenshot: {screenshot_path}')

            # Try to find text editor using JavaScript for more reliable detection
            text_filled = self._fill_text_editor_js(page, text[:3000])

            if not text_filled:
                self.logger.debug('Text editor not found')
                return False

            # Click post button with better detection
            post_button_clicked = False
            post_button_selectors = [
                'button:has-text("Post")',
                '[aria-label="Post"]',
                '[data-testid="post-button"]',
                '.artdeco-button--primary:has-text("Post")',
                '.artdeco-button[aria-label="Post"]',
                'button.artdeco-button--primary:has-text("Post")'
            ]

            for selector in post_button_selectors:
                try:
                    post_buttons = page.query_selector_all(selector)
                    self.logger.debug(f'Trying post button selector: {selector}, found {len(post_buttons)} elements')
                    for button in post_buttons:
                        if button.is_visible():
                            # Check if button is not disabled
                            disabled = button.evaluate('el => el.disabled || el.getAttribute("aria-disabled") === "true"')
                            if not disabled:
                                button.click()
                                self.logger.info(f'✅ Clicked post button with selector: {selector}')
                                time.sleep(5)  # Wait for post to be published
                                post_button_clicked = True
                                break
                    if post_button_clicked:
                        break
                except Exception as e:
                    self.logger.debug(f'Post button attempt ({selector}): {e}')
                    continue

            if not post_button_clicked:
                self.logger.warning('Could not find enabled Post button')
                return False

            return True

        except Exception as e:
            self.logger.debug(f'Post via start box failed: {e}')
            return False
    
    def _fill_text_editor_js(self, page, text: str) -> bool:
        """Fill text editor using JavaScript injection for reliability."""
        try:
            self.logger.info('Attempting to fill LinkedIn text editor...')
            
            # First, let's log what dialogs/editors we can find for debugging
            debug_info = page.evaluate('''
                () => {
                    const dialogs = document.querySelectorAll('div[role="dialog"], div.artdeco-modal');
                    const info = { dialogCount: dialogs.length, editors: [] };
                    
                    for (const dialog of dialogs) {
                        const editors = dialog.querySelectorAll('div[contenteditable="true"], div[role="textbox"], div[contenteditable]');
                        for (const editor of editors) {
                            const rect = editor.getBoundingClientRect();
                            info.editors.push({
                                visible: rect.width > 0 && rect.height > 0,
                                width: rect.width,
                                height: rect.height,
                                hasContent: editor.innerHTML.length > 0
                            });
                        }
                    }
                    return info;
                }
            ''')
            self.logger.info(f'Debug: Found {debug_info.get("dialogCount", 0)} dialogs and {len(debug_info.get("editors", []))} editors')
            
            # Approach 1: Find contenteditable div inside dialog and set innerHTML directly
            self.logger.info('Trying approach 1: Direct innerHTML set with proper events')
            try:
                result = page.evaluate('''
                    () => {
                        const dialogs = document.querySelectorAll('div[role="dialog"], div.artdeco-modal');
                        for (const dialog of dialogs) {
                            const editors = dialog.querySelectorAll('div[contenteditable="true"], div[role="textbox"], div[contenteditable]');
                            for (const editor of editors) {
                                const rect = editor.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    // Clear first
                                    editor.innerHTML = '';
                                    editor.focus();
                                    
                                    // Use InputEvent to notify LinkedIn of changes
                                    const textContent = `{text}`;
                                    
                                    // Try using document.execCommand for better compatibility
                                    document.execCommand('insertText', false, textContent);
                                    
                                    // Also dispatch events
                                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                                    editor.dispatchEvent(new Event('change', { bubbles: true }));
                                    
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                '''.replace('{text}', text.replace('\n', '\\n').replace('`', '\\`').replace('\\', '\\\\')[:2000]))
                
                if result:
                    self.logger.info('✅ Successfully filled editor using approach 1')
                    time.sleep(3)
                    # Verify text was entered
                    verify = page.evaluate('''
                        () => {
                            const editors = document.querySelectorAll('div[contenteditable="true"], div[role="textbox"]');
                            for (const editor of editors) {
                                const rect = editor.getBoundingClientRect();
                                if (rect.width > 0) {
                                    return editor.innerText.length || editor.innerHTML.length;
                                }
                            }
                            return 0;
                        }
                    ''')
                    self.logger.info(f'Verified editor has {verify} characters')
                    return True
            except Exception as e:
                self.logger.debug(f'Approach 1 failed: {e}')

            # Approach 2: Use Playwright's fill method on found element
            self.logger.info('Trying approach 2: Playwright fill method')
            time.sleep(1)
            try:
                editors = page.query_selector_all('div[contenteditable="true"], div[role="textbox"]')
                for editor in editors:
                    try:
                        rect = editor.bounding_box()
                        if rect and rect['width'] > 0 and rect['height'] > 0:
                            editor.click()
                            time.sleep(1)
                            editor.fill(text[:2000])
                            self.logger.info('✅ Successfully filled editor using approach 2')
                            time.sleep(2)
                            return True
                    except Exception as e:
                        self.logger.debug(f'Editor fill attempt failed: {e}')
                        continue
            except Exception as e:
                self.logger.debug(f'Approach 2 failed: {e}')

            # Approach 3: Click editor and use keyboard typing
            self.logger.info('Trying approach 3: Click and keyboard type')
            time.sleep(1)
            try:
                editor_clicked = page.evaluate('''
                    () => {
                        const dialogs = document.querySelectorAll('div[role="dialog"], div.artdeco-modal');
                        for (const dialog of dialogs) {
                            const editors = dialog.querySelectorAll('div[contenteditable="true"], div[role="textbox"], div[contenteditable]');
                            for (const editor of editors) {
                                const rect = editor.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    editor.click();
                                    editor.focus();
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                ''')
                
                if editor_clicked:
                    time.sleep(1.5)
                    # Type text using keyboard - slower but more reliable
                    text_to_type = text[:500]  # Limit for keyboard typing
                    self.logger.info(f'Typing {len(text_to_type)} characters via keyboard...')
                    page.keyboard.type(text_to_type, delay=10)  # Slower typing speed
                    time.sleep(2)
                    return True
            except Exception as e:
                self.logger.debug(f'Approach 3 failed: {e}')

            # Approach 4: Paste from clipboard as final fallback
            self.logger.info('Trying approach 4: Clipboard paste')
            time.sleep(1)
            try:
                # Focus the editor
                page.evaluate('''
                    () => {
                        const dialogs = document.querySelectorAll('div[role="dialog"], div.artdeco-modal');
                        for (const dialog of dialogs) {
                            const editors = dialog.querySelectorAll('div[contenteditable="true"], div[role="textbox"], div[contenteditable]');
                            for (const editor of editors) {
                                const rect = editor.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    editor.focus();
                                    editor.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                ''')
                time.sleep(1)
                
                # Paste from clipboard (Ctrl+A, Delete, Ctrl+V)
                self.logger.info('Pasting from clipboard...')
                page.keyboard.press('Control+A')
                time.sleep(0.3)
                page.keyboard.press('Delete')
                time.sleep(0.3)
                page.keyboard.press('Control+V')
                time.sleep(2)
                return True
            except Exception as e:
                self.logger.debug(f'Approach 4 failed: {e}')

            self.logger.error('All text editor filling approaches failed')
            return False

        except Exception as e:
            self.logger.debug(f'Text editor filling error: {e}')
            return False

    def _post_via_new_post_flow(self, page, text: str) -> bool:
        """Post using alternative flow (navigate to post creation page)."""
        try:
            # Navigate directly to feed
            try:
                page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='domcontentloaded')
            except Exception:
                page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='load')
            time.sleep(5)

            # Try keyboard shortcut to start post
            page.keyboard.press('Shift+O')  # LinkedIn shortcut to start post
            time.sleep(2)

            # Try alternative keyboard shortcut
            if not page.query_selector('div[role="dialog"]'):
                page.keyboard.press('Enter')
                time.sleep(2)

            # Find and fill text editor - try multiple selectors
            text_editor_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"]',
                'div.ql-editor[contenteditable="true"]',
                '[aria-label="Write an article or post"]',
                '[aria-label="Write a post"]',
                'div.ql-editor'
            ]

            for selector in text_editor_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for text_box in elements:
                        if text_box and text_box.is_visible():
                            text_box.fill(text[:3000])
                            self.logger.info(f'Filled text editor in alternative flow with: {selector}')
                            time.sleep(1.5)

                            # Find and click post button
                            post_button_selectors = [
                                'button:has-text("Post")',
                                '[aria-label="Post"]',
                                '[data-testid="post-button"]',
                                '.artdeco-button--primary:has-text("Post")'
                            ]
                            
                            for post_selector in post_button_selectors:
                                post_buttons = page.query_selector_all(post_selector)
                                for button in post_buttons:
                                    if button.is_visible():
                                        button.click()
                                        self.logger.info(f'Clicked post button in alternative flow with: {post_selector}')
                                        time.sleep(3)
                                        return True
                except Exception as e:
                    self.logger.debug(f'Text editor attempt ({selector}): {e}')
                    continue

            return False

        except Exception as e:
            self.logger.debug(f'Alternative post flow failed: {e}')
            return False

    def log_post(self, post_data: dict, success: bool):
        """Log the posting result."""
        log_file = self.logs_folder / 'linkedin_posts.json'

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []

        # Add new entry - handle both draft generation and execution log formats
        log_entry = {
            'timestamp': post_data.get('timestamp', post_data.get('executed_at', datetime.now().isoformat())),
            'category': post_data.get('category', 'unknown'),
            'hashtags': post_data.get('hashtags', []),
            'text_preview': post_data.get('text_preview', ''),
            'success': success
        }
        
        # Add execution-specific fields if present
        if 'approval_file' in post_data:
            log_entry['approval_file'] = post_data['approval_file']
        if 'draft_file' in post_data:
            log_entry['draft_file'] = post_data['draft_file']

        logs.append(log_entry)

        log_file.write_text(json.dumps(logs, indent=2))

    def run_generate_only(self, category: str = None) -> Path:
        """
        Generate a post draft without posting.

        Args:
            category: Optional post category

        Returns:
            Path: Path to the created draft
        """
        self.logger.info('Generating LinkedIn post draft...')

        # Generate post
        post_data = self.generate_post(category)

        # Create draft file
        draft_path = self.create_draft_file(post_data)

        self.logger.info(f'Draft created: {draft_path.name}')
        return draft_path

    def run_with_approval(self, category: str = None) -> Path:
        """
        Generate post and create approval request.

        Args:
            category: Optional post category

        Returns:
            Path: Path to the approval request
        """
        self.logger.info('Generating LinkedIn post with approval workflow...')

        # Generate post
        post_data = self.generate_post(category)

        # Create draft
        draft_path = self.create_draft_file(post_data)

        # Create approval request
        approval_path = self.create_approval_request(draft_path)

        self.logger.info(f'Approval request created: {approval_path.name}')
        return approval_path

    def execute_approved_post(self) -> bool:
        """
        Execute all approved LinkedIn posts.

        Scans the Approved/LinkedIn folder for approved posts,
        publishes them, and moves to Done folder.

        Returns:
            bool: True if any posts were executed
        """
        self.logger.info('Checking for approved LinkedIn posts...')

        if not self.approved_folder.exists():
            self.logger.info('No approved folder found')
            return False

        # Find approved post files
        approved_files = list(self.approved_folder.glob('POST_*.md'))

        if not approved_files:
            self.logger.info('No approved posts found')
            return False

        self.logger.info(f'Found {len(approved_files)} approved post(s) to publish')

        success_count = 0
        failed_count = 0

        for approval_file in approved_files:
            try:
                self.logger.info(f'Processing: {approval_file.name}')

                # Parse approval file to get draft info
                content = approval_file.read_text(encoding='utf-8')

                # Extract draft file reference from frontmatter
                draft_file_name = None
                for line in content.split('\n')[:20]:
                    if line.startswith('draft_file:'):
                        draft_file_name = line.split(':', 1)[1].strip()
                        break

                if draft_file_name:
                    # Find and read the draft file
                    draft_path = self.drafts_folder / draft_file_name
                    if draft_path.exists():
                        draft_content = draft_path.read_text(encoding='utf-8')

                        # Extract the actual post content
                        post_text = self._extract_post_content(draft_content)

                        if post_text:
                            # Post to LinkedIn
                            success = self.post_to_linkedin(post_text)

                            # Extract category from draft for logging
                            draft_category = 'unknown'
                            for line in draft_content.split('\n')[:20]:
                                if line.startswith('category:'):
                                    draft_category = line.split(':', 1)[1].strip()
                                    break

                            # Log the result
                            self.log_post({
                                'text_preview': post_text[:100] + '...',
                                'category': draft_category,
                                'hashtags': [],
                                'approval_file': approval_file.name,
                                'draft_file': draft_file_name,
                                'executed_at': datetime.now().isoformat()
                            }, success)

                            if success:
                                # Move approval file to Done
                                done_folder = self.vault_path / 'Done' / 'LinkedIn'
                                done_folder.mkdir(parents=True, exist_ok=True)
                                approval_file.rename(done_folder / approval_file.name)

                                self.logger.info(f'✅ Published: {draft_file_name}')
                                success_count += 1
                            else:
                                self.logger.error(f'❌ Failed to publish: {draft_file_name}')
                                failed_count += 1
                        else:
                            self.logger.error(f'Could not extract post content from {draft_file_name}')
                            failed_count += 1
                    else:
                        self.logger.error(f'Draft file not found: {draft_file_name}')
                        failed_count += 1
                else:
                    self.logger.warning(f'No draft file reference in {approval_file.name}')
                    failed_count += 1

            except Exception as e:
                self.logger.error(f'Error processing {approval_file.name}: {e}')
                failed_count += 1

        # Summary
        self.logger.info(f'')
        self.logger.info(f'Execution Summary:')
        self.logger.info(f'  Total: {len(approved_files)}')
        self.logger.info(f'  Published: {success_count}')
        self.logger.info(f'  Failed: {failed_count}')
        self.logger.info(f'')

        return success_count > 0

    def _extract_post_content(self, draft_content: str) -> str:
        """
        Extract the actual post content from a draft file.

        Args:
            draft_content: Full draft file content

        Returns:
            str: The LinkedIn post text, or empty string
        """
        try:
            # Look for "## Content" section
            if '## Content' in draft_content:
                parts = draft_content.split('## Content', 1)
                if len(parts) > 1:
                    # Get content until next ## section
                    content_part = parts[1]
                    if '## Metadata' in content_part:
                        content_part = content_part.split('## Metadata')[0]
                    return content_part.strip()

            # Fallback: return empty string
            return ''

        except Exception as e:
            self.logger.error(f'Error extracting post content: {e}')
            return ''


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='LinkedIn Auto-Poster for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # First-time setup (authenticate with LinkedIn)
  python skills/linkedin_auth.py --login

  # Generate a draft post for review
  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate

  # Generate with approval workflow
  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post

  # Publish all approved posts
  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --execute-approved

  # Check LinkedIn authentication status
  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --check-auth
        '''
    )

    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--generate', action='store_true',
                        help='Generate draft only')
    parser.add_argument('--post', action='store_true',
                        help='Generate with approval workflow')
    parser.add_argument('--execute-approved', action='store_true',
                        help='Publish all approved posts')
    parser.add_argument('--check-auth', action='store_true',
                        help='Check LinkedIn authentication status')
    parser.add_argument('--category', type=str, default=None,
                        choices=['service_announcement', 'success_story',
                               'industry_insight', 'behind_the_scenes',
                               'thought_leadership'],
                        help='Post category')
    parser.add_argument('--session-path', type=str, default=None,
                        help='Path to LinkedIn browser session')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging('LinkedInPoster')

    try:
        poster = LinkedInPoster(
            vault_path=args.vault,
            session_path=args.session_path,
            headless=args.headless
        )

        # Check authentication status
        if args.check_auth:
            if poster.auth.has_valid_session():
                print('✅ LinkedIn authentication is active')
                print(f'   Session stored at: {poster.session_path}')
                sys.exit(0)
            else:
                print('⚠️  No LinkedIn session found')
                print('   Run: python skills/linkedin_auth.py --login')
                sys.exit(1)

        # Generate draft only
        if args.generate:
            draft_path = poster.run_generate_only(args.category)
            print(f'✅ Draft created: {draft_path}')
            print(f'   Review at: {draft_path}')
            print(f'')
            print(f'Next steps:')
            print(f'  1. Review and edit the draft file')
            print(f'  2. Run with --post to create approval request')
            print(f'  3. Move approval to Approved/LinkedIn/ to publish')
            sys.exit(0)

        # Generate with approval workflow
        elif args.post:
            approval_path = poster.run_with_approval(args.category)
            print(f'✅ Approval request created: {approval_path}')
            print(f'')
            print(f'Next steps:')
            print(f'  1. Review the draft (created in Drafts/LinkedIn/)')
            print(f'  2. If satisfied, move approval file to: Approved/LinkedIn/')
            print(f'  3. Run with --execute-approved to publish')
            sys.exit(0)

        # Execute approved posts
        elif args.execute_approved:
            success = poster.execute_approved_post()
            if success:
                print(f'✅ Approved posts published')
                sys.exit(0)
            else:
                print(f'⚠️  No posts were published (check logs for details)')
                sys.exit(1)

        else:
            print('LinkedIn Auto-Poster - Generate and publish business content')
            print('')
            print('Usage:')
            print('  --generate          Create a draft post for review')
            print('  --post              Create draft + approval request')
            print('  --execute-approved  Publish all approved posts')
            print('  --check-auth        Check LinkedIn login status')
            print('  --category TYPE     Specify post category')
            print('')
            print('Available categories:')
            print('  service_announcement, success_story, industry_insight,')
            print('  behind_the_scenes, thought_leadership')
            print('')
            print('First time? Run authentication first:')
            print('  python skills/linkedin_auth.py --login')
            print('')
            print('Examples:')
            print('  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate')
            print('  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post --category success_story')
            print('  python skills/linkedin_poster.py --vault ./AI_Employee_Vault --execute-approved')
            sys.exit(0)

    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
