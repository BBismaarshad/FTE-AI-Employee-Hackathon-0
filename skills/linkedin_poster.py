"""
LinkedIn Auto-Poster - Generate and post business content to LinkedIn.

This skill:
1. Generates professional LinkedIn posts about your business
2. Creates draft files for human review
3. Posts approved content using Playwright automation
4. Tracks posts and engagement in logs

Usage:
    python skills/linkedin_poster.py --vault /path/to/vault --generate

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
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher, setup_logging

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

        # Setup folders
        self.drafts_folder = self.vault_path / 'Drafts' / 'LinkedIn'
        self.drafts_folder.mkdir(parents=True, exist_ok=True)

        self.pending_approval = self.vault_path / 'Pending_Approval' / 'LinkedIn'
        self.pending_approval.mkdir(parents=True, exist_ok=True)

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
        draft_path.write_text(content)
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
        draft_content = draft_path.read_text()

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
        approval_path.write_text(content)
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
            with sync_playwright() as p:
                # Launch browser
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 720}
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com', timeout=60000)

                # Wait for page to load (check for login or feed)
                try:
                    page.wait_for_selector('[data-testid="share-box-start-post-creation-button"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.warning('Post creation button not found - may need login')
                    # Check if login is required
                    if 'login' in page.url.lower():
                        self.logger.error('LinkedIn login required! Please login manually first run.')
                        context.close()
                        return False

                # Start post creation
                post_button = page.query_selector(
                    '[data-testid="share-box-start-post-creation-button"]'
                )
                if post_button:
                    post_button.click()
                    time.sleep(2)

                    # Find text editor and type content
                    text_areas = page.query_selector_all('div[role="textbox"]')
                    if text_areas:
                        text_areas[0].fill(text[:3000])  # LinkedIn has 3000 char limit
                        time.sleep(1)

                        # Click post button
                        post_buttons = page.query_selector_all('button:has-text("Post")')
                        if post_buttons:
                            post_buttons[0].click()
                            time.sleep(3)
                            self.logger.info('LinkedIn post published successfully!')
                            context.close()
                            return True

                self.logger.error('Failed to post - UI elements not found')
                context.close()
                return False

        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
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

        # Add new entry
        logs.append({
            'timestamp': datetime.now().isoformat(),
            'category': post_data['category'],
            'hashtags': post_data['hashtags'],
            'text_preview': post_data['text'][:100] + '...',
            'success': success
        })

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


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Auto-Poster for AI Employee')
    parser.add_argument('--vault', type=str, required=True,
                        help='Path to Obsidian vault')
    parser.add_argument('--generate', action='store_true',
                        help='Generate draft only')
    parser.add_argument('--post', action='store_true',
                        help='Generate with approval workflow')
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

        if args.generate:
            draft_path = poster.run_generate_only(args.category)
            print(f'✅ Draft created: {draft_path}')

        elif args.post:
            approval_path = poster.run_with_approval(args.category)
            print(f'✅ Approval request created: {approval_path}')

        else:
            print('Use --generate or --post flag')
            print('Examples:')
            print('  python linkedin_poster.py --vault /path/to/vault --generate')
            print('  python linkedin_poster.py --vault /path/to/vault --post')

    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
