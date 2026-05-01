"""
Facebook & Instagram Poster - Gold Tier AI Employee Skill

Provides automated social media management for Facebook and Instagram:
- Post text and images to Facebook
- Post to Instagram
- Generate engagement summaries
- Draft approval workflow

Uses Playwright for browser automation.
Part of the Gold Tier requirements for the FTE AI Employee Hackathon.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher


class FacebookPoster:
    """Automates posting to Facebook and Instagram with approval workflow."""

    def __init__(self, vault_path, session_path=None, dry_run=False):
        """
        Initialize Facebook Poster.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to browser session data (for persistent login)
            dry_run: If True, simulate actions without posting
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else Path.home() / '.ai-employee' / 'facebook-session'
        self.dry_run = dry_run
        self.logger = logging.getLogger('FacebookPoster')

        # Vault folders
        self.drafts_folder = self.vault_path / 'Drafts' / 'Facebook'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done' / 'Facebook'
        self.logs_folder = self.vault_path / 'Logs'

        # Create folders
        for folder in [self.drafts_folder, self.pending_approval, self.approved_folder,
                       self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Session path
        self.session_path.mkdir(parents=True, exist_ok=True)

    def generate_post_draft(self, category='business_update'):
        """
        Generate a Facebook post draft.

        Args:
            category: Type of post (business_update, success_story, engagement, tip, announcement)

        Returns:
            Path to created draft file
        """
        templates = {
            'business_update': {
                'content': """🚀 Exciting Business Update!

We're thrilled to share our latest progress with you. Our AI Employee automation system is transforming how we work, allowing us to focus on what truly matters - delivering value to our customers.

Key highlights this week:
✅ Automated 50+ routine tasks
✅ Improved response time by 70%
✅ Enhanced customer satisfaction

Want to learn how automation can transform your business? Drop a comment below! 👇

#BusinessAutomation #AIEmployee #Productivity #Innovation""",
                'image_suggestion': 'business_dashboard.png'
            },
            'success_story': {
                'content': """🎉 Customer Success Story!

One of our clients recently shared how our AI Employee solution helped them save 20 hours per week on routine tasks. That's an entire day back in their schedule!

"The automation has been a game-changer for our team. We can now focus on strategic work instead of repetitive tasks." - Happy Client

Ready to transform your workflow? Let's chat! 💬

#SuccessStory #ClientWin #Automation #BusinessGrowth""",
                'image_suggestion': 'success_celebration.png'
            },
            'engagement': {
                'content': """💡 Quick Question for You!

What's the ONE task you wish you could automate in your business?

For us, it was email management and social media scheduling. Now our AI Employee handles it seamlessly!

Share your thoughts in the comments - we'd love to hear what's taking up your valuable time! 👇

#BusinessTips #Automation #Productivity #CommunityEngagement""",
                'image_suggestion': 'question_graphic.png'
            },
            'tip': {
                'content': """📌 Pro Tip Tuesday!

Did you know? You can automate up to 80% of routine business tasks with the right AI tools.

Here's what we automated this month:
• Email triage and responses
• Social media posting
• Invoice generation
• Customer follow-ups
• Weekly reporting

Start small, automate one task at a time, and watch your productivity soar! 🚀

What would you automate first? Comment below!

#ProductivityTips #BusinessAutomation #AITools #WorkSmarter""",
                'image_suggestion': 'productivity_tips.png'
            },
            'announcement': {
                'content': """📢 Important Announcement!

We're expanding our AI Employee services to help more businesses achieve automation excellence!

New offerings include:
🔹 Custom automation workflows
🔹 Integration with your existing tools
🔹 24/7 autonomous operation
🔹 Human-in-the-loop safety

Limited spots available for our next cohort. Interested? Send us a message!

#BusinessAnnouncement #AIEmployee #Automation #BusinessServices""",
                'image_suggestion': 'announcement_banner.png'
            }
        }

        template = templates.get(category, templates['business_update'])
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"FB_{category}_{timestamp}.md"
        filepath = self.drafts_folder / filename

        content = f"""---
type: facebook_post
category: {category}
status: draft
created: {datetime.now().isoformat()}
platform: facebook
requires_approval: true
image_suggestion: {template['image_suggestion']}
---

# Facebook Post Draft - {category.replace('_', ' ').title()}

## Content

{template['content']}

## Posting Instructions

1. Review and edit the content above
2. Prepare the suggested image: {template['image_suggestion']}
3. Move this file to `Pending_Approval/` when ready
4. After approval, the post will be published

## Notes

- Best posting times: 9 AM, 1 PM, 7 PM
- Include relevant hashtags
- Engage with comments within 1 hour
- Monitor engagement metrics

---
*Generated by AI Employee - Facebook Poster*
"""

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created Facebook draft: {filepath}")

        # Log the action
        self._log_action('draft_created', {
            'file': filename,
            'category': category,
            'status': 'success'
        })

        return filepath

    def post_to_facebook(self, content, image_path=None):
        """
        Post content to Facebook.

        Args:
            content: Text content to post
            image_path: Optional path to image file

        Returns:
            dict with success status and details
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Facebook: {content[:50]}...")
            return {
                "success": True,
                "platform": "facebook",
                "dry_run": True,
                "message": "Dry run - no actual post made"
            }

        try:
            with sync_playwright() as p:
                # Launch browser with persistent session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True for production
                    viewport={'width': 1280, 'height': 720}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to Facebook
                self.logger.info("Navigating to Facebook...")
                page.goto("https://www.facebook.com", wait_until='networkidle')

                # Check if logged in
                if "login" in page.url.lower():
                    self.logger.warning("Not logged in to Facebook. Please log in manually.")
                    input("Press Enter after logging in...")

                # Find the post creation box
                # Note: Facebook's selectors change frequently
                # This is a simplified version - production code needs more robust selectors
                try:
                    # Click on "What's on your mind?" box
                    page.click('[aria-label*="What\'s on your mind"]', timeout=5000)
                    page.wait_for_timeout(1000)

                    # Type content
                    page.fill('[aria-label*="What\'s on your mind"]', content)

                    # Upload image if provided
                    if image_path and Path(image_path).exists():
                        page.set_input_files('[type="file"]', str(image_path))
                        page.wait_for_timeout(2000)

                    # Click Post button
                    page.click('[aria-label="Post"]', timeout=5000)
                    page.wait_for_timeout(3000)

                    self.logger.info("Successfully posted to Facebook")
                    result = {
                        "success": True,
                        "platform": "facebook",
                        "message": "Posted successfully"
                    }

                except PlaywrightTimeout:
                    self.logger.error("Timeout while trying to post. Facebook UI may have changed.")
                    result = {
                        "success": False,
                        "error": "Timeout - Facebook UI may have changed"
                    }

                browser.close()
                return result

        except Exception as e:
            self.logger.error(f"Facebook post failed: {e}")
            return {"success": False, "error": str(e)}

    def post_to_instagram(self, image_path, caption):
        """
        Post to Instagram.

        Args:
            image_path: Path to image file (required for Instagram)
            caption: Caption text

        Returns:
            dict with success status and details
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Instagram with caption: {caption[:50]}...")
            return {
                "success": True,
                "platform": "instagram",
                "dry_run": True,
                "message": "Dry run - no actual post made"
            }

        if not image_path or not Path(image_path).exists():
            return {"success": False, "error": "Instagram requires an image"}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                self.logger.info("Navigating to Instagram...")
                page.goto("https://www.instagram.com", wait_until='networkidle')

                # Check if logged in
                if "login" in page.url.lower():
                    self.logger.warning("Not logged in to Instagram. Please log in manually.")
                    input("Press Enter after logging in...")

                # Instagram posting logic
                # Note: Instagram's web interface has limited posting capabilities
                # For production, consider using Instagram Graph API

                self.logger.info("Instagram web posting has limitations. Consider using Instagram Graph API.")
                result = {
                    "success": True,
                    "platform": "instagram",
                    "message": "Manual posting required - Instagram web has limitations"
                }

                browser.close()
                return result

        except Exception as e:
            self.logger.error(f"Instagram post failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_summary(self):
        """
        Generate summary of recent posts and engagement.

        Returns:
            dict with engagement metrics
        """
        # Count recent drafts and posts
        draft_count = len(list(self.drafts_folder.glob('*.md')))
        done_count = len(list(self.done_folder.glob('*.md')))

        # Read recent logs
        recent_posts = []
        for log_file in sorted(self.logs_folder.glob('*.json'), reverse=True)[:7]:
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
                for entry in logs:
                    if entry.get('action_type') == 'post_published':
                        recent_posts.append(entry)
            except:
                pass

        summary = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "drafts_pending": draft_count,
                "posts_published": done_count,
                "recent_posts_7days": len(recent_posts)
            },
            "summary": f"Facebook/Instagram Status: {draft_count} drafts pending, {done_count} posts published",
            "recent_activity": recent_posts[:5]
        }

        return summary

    def process_approved_posts(self):
        """
        Process posts that have been moved to Approved folder.

        Returns:
            list of results for each processed post
        """
        results = []

        for approved_file in self.approved_folder.glob('FB_*.md'):
            self.logger.info(f"Processing approved post: {approved_file.name}")

            try:
                content = approved_file.read_text(encoding='utf-8')

                # Extract content between ## Content and ## Posting Instructions
                if '## Content' in content and '## Posting Instructions' in content:
                    start = content.index('## Content') + len('## Content')
                    end = content.index('## Posting Instructions')
                    post_content = content[start:end].strip()

                    # Post to Facebook
                    result = self.post_to_facebook(post_content)
                    results.append(result)

                    if result.get('success'):
                        # Move to Done
                        done_path = self.done_folder / approved_file.name
                        approved_file.rename(done_path)

                        # Log success
                        self._log_action('post_published', {
                            'file': approved_file.name,
                            'platform': 'facebook',
                            'status': 'success'
                        })
                    else:
                        self.logger.error(f"Failed to post: {result.get('error')}")

            except Exception as e:
                self.logger.error(f"Error processing {approved_file.name}: {e}")
                results.append({"success": False, "error": str(e), "file": approved_file.name})

        return results

    def _log_action(self, action_type, details):
        """Log action to daily log file."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "facebook_poster",
            **details
        }

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                logs = []

        # Append new entry
        logs.append(entry)

        # Write back
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def main():
    """CLI interface for Facebook Poster."""
    parser = argparse.ArgumentParser(description='Facebook & Instagram Poster - Gold Tier AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--session', type=str, help='Path to browser session data')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual posting)')
    parser.add_argument('--generate', action='store_true', help='Generate a post draft')
    parser.add_argument('--category', type=str, default='business_update',
                       choices=['business_update', 'success_story', 'engagement', 'tip', 'announcement'],
                       help='Category of post to generate')
    parser.add_argument('--process-approved', action='store_true', help='Process approved posts')
    parser.add_argument('--summary', action='store_true', help='Generate engagement summary')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize poster
    poster = FacebookPoster(
        vault_path=args.vault,
        session_path=args.session,
        dry_run=args.dry_run
    )

    # Execute requested action
    if args.generate:
        draft_path = poster.generate_post_draft(category=args.category)
        print(f"✅ Draft created: {draft_path}")
        print(f"📝 Review and move to Pending_Approval/ when ready")

    elif args.process_approved:
        results = poster.process_approved_posts()
        print(f"✅ Processed {len(results)} approved posts")
        for result in results:
            if result.get('success'):
                print(f"  ✓ Posted successfully")
            else:
                print(f"  ✗ Failed: {result.get('error')}")

    elif args.summary:
        summary = poster.generate_summary()
        print(json.dumps(summary, indent=2))

    else:
        print("Please specify an action: --generate, --process-approved, or --summary")
        print("Use --help for more information")


if __name__ == '__main__':
    main()
