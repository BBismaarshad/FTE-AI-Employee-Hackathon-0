# Facebook & Instagram Poster - Agent Skill

**Tier:** Gold  
**Category:** Social Media Automation  
**Status:** ✅ Ready

## Overview

Automated social media management for Facebook and Instagram with human-in-the-loop approval workflow. Generates professional post drafts, manages posting, and tracks engagement metrics.

## Features

- 📝 **Post Draft Generation** - 5 content categories
- 🎨 **Template System** - Customizable post templates
- ✅ **Approval Workflow** - Human oversight for all posts
- 📊 **Engagement Tracking** - Summary reports
- 🤖 **Browser Automation** - Playwright-based posting
- 📁 **Vault Integration** - Full Obsidian integration

## Installation

### Prerequisites

```bash
# Playwright already installed from Silver Tier
playwright install chromium
```

### Verify Installation

```bash
python skills/facebook_poster.py --help
```

## Usage

### Generate Post Draft

```bash
# Generate a business update post
python skills/facebook_poster.py --vault .\AI_Employee_Vault --generate --category business_update

# Available categories:
# - business_update
# - success_story
# - engagement
# - tip
# - announcement
```

### Process Approved Posts

```bash
# Post all approved drafts
python skills/facebook_poster.py --vault .\AI_Employee_Vault --process-approved

# Dry run mode (test without posting)
python skills/facebook_poster.py --vault .\AI_Employee_Vault --process-approved --dry-run
```

### Generate Engagement Summary

```bash
python skills/facebook_poster.py --vault .\AI_Employee_Vault --summary
```

## Workflow

### 1. Draft Creation

```
AI generates draft → Saved to Drafts/Facebook/
```

### 2. Review & Approval

```
Review draft → Edit if needed → Move to Pending_Approval/
```

### 3. Posting

```
Run --process-approved → Posts to Facebook → Moves to Done/Facebook/
```

### 4. Tracking

```
All actions logged to Logs/YYYY-MM-DD.json
```

## Post Categories

### Business Update
Professional updates about company progress and achievements.

**Template includes:**
- Progress highlights
- Key metrics
- Call to action
- Relevant hashtags

### Success Story
Customer testimonials and case studies.

**Template includes:**
- Client quote
- Results achieved
- Social proof
- Engagement prompt

### Engagement
Questions and polls to drive community interaction.

**Template includes:**
- Thought-provoking question
- Personal experience
- Comment prompt
- Community hashtags

### Tip
Educational content and best practices.

**Template includes:**
- Actionable advice
- Bullet points
- Pro tips
- Value-focused hashtags

### Announcement
Important business announcements and launches.

**Template includes:**
- Clear announcement
- Key details
- Call to action
- Announcement hashtags

## Configuration

### Custom Session Path

```bash
python skills/facebook_poster.py --vault .\AI_Employee_Vault --session C:\custom\path --generate
```

### Dry Run Mode

Always test with `--dry-run` before posting:

```bash
python skills/facebook_poster.py --vault .\AI_Employee_Vault --process-approved --dry-run
```

## Vault Structure

```
AI_Employee_Vault/
├── Drafts/
│   └── Facebook/
│       └── FB_business_update_2026-05-01_120000.md
├── Pending_Approval/
│   └── FB_business_update_2026-05-01_120000.md
├── Approved/
│   └── (Posts ready to publish)
├── Done/
│   └── Facebook/
│       └── (Published posts)
└── Logs/
    └── 2026-05-01.json
```

## First-Time Setup

### 1. Login to Facebook

```bash
python skills/facebook_poster.py --vault .\AI_Employee_Vault --generate
```

On first run:
1. Browser opens to Facebook
2. Log in manually
3. Session saved for future use

### 2. Test Posting

```bash
# Generate a test draft
python skills/facebook_poster.py --vault .\AI_Employee_Vault --generate --category tip

# Review the draft in Drafts/Facebook/

# Move to Pending_Approval/ when ready

# Test with dry run
python skills/facebook_poster.py --vault .\AI_Employee_Vault --process-approved --dry-run
```

## Best Practices

### Posting Schedule

- **Morning:** 9:00 AM - High engagement
- **Lunch:** 1:00 PM - Good reach
- **Evening:** 7:00 PM - Peak engagement

### Content Mix

- 40% Educational (tips, insights)
- 30% Engagement (questions, polls)
- 20% Promotional (services, announcements)
- 10% Personal (behind-the-scenes, stories)

### Engagement

- Respond to comments within 1 hour
- Like and reply to all comments
- Monitor post performance
- Adjust strategy based on metrics

## Troubleshooting

### Issue: "Not logged in to Facebook"

**Solution:**
1. Run with `--dry-run` first
2. Browser will open
3. Log in manually
4. Session will be saved

### Issue: "Timeout while trying to post"

**Cause:** Facebook UI changed

**Solution:**
1. Check Facebook's current UI
2. Update selectors in code if needed
3. Use dry-run mode to test

### Issue: "No drafts found"

**Solution:**
1. Generate drafts first: `--generate`
2. Check `Drafts/Facebook/` folder exists
3. Verify vault path is correct

### Issue: "Unicode encoding error"

**Solution:** Already fixed - all files use UTF-8 encoding

## Security Notes

- ⚠️ **Never commit session data** - Added to .gitignore
- ✅ **Use approval workflow** - All posts require review
- 📝 **Audit logging** - All actions logged
- 🔒 **Session isolation** - Separate browser profile

## Integration with Orchestrator

The orchestrator can automatically:
1. Generate drafts on schedule
2. Process approved posts
3. Generate weekly summaries

Add to scheduled tasks:
```powershell
# Generate daily post draft
schtasks /create /tn "AI_Employee_Facebook_Draft" /tr "python skills\facebook_poster.py --vault .\AI_Employee_Vault --generate" /sc daily /st 08:00
```

## API Limitations

### Facebook Web Automation

- ⚠️ **Rate Limits:** Avoid posting more than 5 times per day
- ⚠️ **UI Changes:** Facebook UI changes frequently
- ⚠️ **Detection:** Use realistic delays between actions

### Instagram

- ⚠️ **Limited Web API:** Instagram web has posting limitations
- 💡 **Recommendation:** Use Instagram Graph API for production
- 📱 **Alternative:** Manual posting via mobile app

## Advanced Usage

### Custom Templates

Edit templates in `facebook_poster.py`:

```python
templates = {
    'custom_category': {
        'content': """Your custom template here""",
        'image_suggestion': 'custom_image.png'
    }
}
```

### Scheduled Posting

Combine with Windows Task Scheduler:

```powershell
# Morning post
schtasks /create /tn "FB_Morning" /tr "python skills\facebook_poster.py --vault .\AI_Employee_Vault --process-approved" /sc daily /st 09:00

# Evening post
schtasks /create /tn "FB_Evening" /tr "python skills\facebook_poster.py --vault .\AI_Employee_Vault --process-approved" /sc daily /st 19:00
```

## Metrics & Analytics

Track performance in logs:

```json
{
  "timestamp": "2026-05-01T12:00:00",
  "action_type": "post_published",
  "platform": "facebook",
  "category": "business_update",
  "status": "success"
}
```

## Support

- 📚 **Documentation:** This file
- 🐛 **Issues:** Check logs in `Logs/` folder
- 💬 **Community:** Wednesday Research Meetings

## Related Skills

- **LinkedIn Auto-Poster** - Similar workflow for LinkedIn
- **Weekly Audit** - Includes social media metrics
- **Email MCP Server** - Notification system

---

**Built for Gold Tier - FTE AI Employee Hackathon**  
**Part of the autonomous social media management system**
