# LinkedIn Auto-Poster Skill

Automatically generate and post business-focused content to LinkedIn to generate sales.

## Overview

This skill enables your AI Employee to autonomously create, review, and post business content on LinkedIn. It generates professional posts about your services, success stories, and industry insights to attract potential clients and generate leads.

## Features

- **Content Generation**: Creates professional LinkedIn posts about your business
- **Topic Rotation**: Cycles through multiple content categories:
  - Service announcements
  - Client success stories  
  - Industry insights/tips
  - Behind-the-scenes updates
  - Thought leadership posts
- **Human-in-the-Loop**: Drafts posts for approval before publishing (Silver tier)
- **Scheduling**: Supports scheduled posting times
- **Hashtag Optimization**: Includes relevant hashtags for reach
- **Brand Voice**: Follows your company handbook's tone and style guidelines
- **Engagement Tracking**: Logs posts and tracks engagement metrics

## Prerequisites

1. **LinkedIn Account**: Active LinkedIn profile or company page
2. **Python Dependencies**:
   ```bash
   pip install playwright
   playwright install chromium
   ```
3. **LinkedIn Session**: Saved browser session or credentials
4. **Content Guidelines**: Define your brand voice in `Company_Handbook.md`

## Installation

1. Ensure all prerequisites are installed
2. Copy `linkedin_poster.py` to the `watchers/` or `skills/` directory
3. Update your `Company_Handbook.md` with LinkedIn guidelines
4. First run will require LinkedIn login (session saved for future runs)

## Usage

### Generate Post Only (Draft Mode)
```bash
python skills/linkedin_poster.py --vault /path/to/vault --generate
```

### Post with Approval
```bash
python skills/linkedin_poster.py --vault /path/to/vault --post
```

### Scheduled Posting
```bash
python skills/linkedin_poster.py --vault /path/to/vault --schedule "09:00"
```

### Custom Topic
```bash
python skills/linkedin_poster.py --vault /path/to/vault --topic "success_story"
```

## Content Categories

### 1. Service Announcement
Promote your services and offerings:
```
🚀 Excited to announce our new AI automation consulting service!

We help businesses save 20+ hours per week by automating repetitive tasks with cutting-edge AI solutions.

👉 DM me to learn how we can transform your workflow.

#AIAutomation #BusinessEfficiency #Innovation
```

### 2. Client Success Story
Share anonymized results:
```
📊 Client Success Story:

A local business was spending 15 hours/week on manual data entry.

We implemented an AI-powered solution that:
✅ Reduced processing time by 85%
✅ Cut errors by 95%
✅ Saved $3,000/month in labor costs

The result? They can now focus on growing their business instead of managing spreadsheets.

Ready to transform your operations? Let's talk!

#CaseStudy #AIResults #BusinessGrowth
```

### 3. Industry Insight
Share valuable knowledge:
```
💡 Quick Tip for Business Owners:

Did you know? 80% of repetitive business tasks can be automated with existing AI tools.

Top 3 tasks to automate first:
1️⃣ Email responses & scheduling
2️⃣ Invoice generation & tracking
3️⃣ Customer follow-ups

What's the one task you wish you could automate today?

#BusinessTips #Automation #Productivity
```

### 4. Behind-the-Scenes
Humanize your brand:
```
🔧 Behind the Scenes:

Working on something exciting today - building an AI system that will help a client automatically process 500+ invoices per month!

Love solving real-world problems with technology.

This is what innovation looks like! 💪

#TechLife #Innovation #BuildingTheFuture
```

## How It Works

1. **Content Planning**:
   - Reads `Business_Goals.md` for active services/campaigns
   - Selects content category based on posting schedule
   - Generates post using AI with brand voice guidelines

2. **Draft Creation**:
   - Creates markdown draft in `/Vault/Drafts/LinkedIn/`
   - Includes post text, hashtags, and optional image suggestions
   - Adds metadata (category, scheduled time, status)

3. **Approval Workflow** (Silver tier):
   - Moves draft to `/Vault/Pending_Approval/`
   - Waits for human approval
   - Can be approved/rejected via file movement

4. **Posting** (with approval):
   - Uses Playwright to access LinkedIn
   - Creates new post with approved content
   - Confirms successful posting
   - Logs post to `/Vault/Logs/linkedin_posts.json`

5. **Tracking**:
   - Updates dashboard with recent posts
   - Tracks engagement metrics (if accessible)
   - Maintains posting history

## File Structure

```
/Vault/
  Drafts/
    LinkedIn/
      - 2026-04-06_service_announcement.md
  Pending_Approval/
    LinkedIn/
      - POST_2026-04-06_pending.md
  Approved/
    LinkedIn/
      - POST_2026-04-06_approved.md
  Logs/
    - linkedin_posts.json
```

## Draft File Format

```markdown
---
type: linkedin_draft
category: service_announcement
created: 2026-04-06T09:00:00
status: pending_approval
scheduled_time: 2026-04-06T10:00:00
hashtags: "#AIAutomation #BusinessEfficiency #Innovation"
estimated_reach: professional
---

# LinkedIn Post Draft

## Content
🚀 Excited to announce our new AI automation consulting service!

We help businesses save 20+ hours per week by automating repetitive tasks with cutting-edge AI solutions.

👉 DM me to learn how we can transform your workflow.

#AIAutomation #BusinessEfficiency #Innovation

## Suggested Image
Optional: Screenshot of AI dashboard or workflow diagram

## Notes
- Target audience: Small business owners
- Goal: Generate leads for consulting
- Tone: Professional but approachable

---
*Generated by AI Employee at 2026-04-06 09:00*
```

## Security Notes

- **LinkedIn Terms of Service**: Automated posting may violate LinkedIn's ToS
- **Use at Your Own Risk**: Consider using LinkedIn's official API or scheduling tools
- **Session Security**: Browser sessions are stored locally - protect them
- **Content Review**: Always review AI-generated posts before publishing
- **Rate Limiting**: Avoid posting too frequently (recommended: 1-3 posts/day max)
- **Professional Standards**: Maintain professional tone and accuracy

## Configuration

### Company Handbook Updates

Add LinkedIn guidelines to your `Company_Handbook.md`:

```markdown
## LinkedIn Posting Guidelines
- Post frequency: 3 times per week
- Best posting times: 9-10 AM, 12-1 PM (your timezone)
- Tone: Professional, helpful, not overly salesy
- Avoid: Controversial topics, competitor mentions
- Include: Call-to-action in every post
- Hashtags: 3-5 relevant hashtags per post
```

### Business Goals Integration

Update `Business_Goals.md` to guide content:

```markdown
## Current Campaigns
- AI Automation Consulting (Q1 2026)
- Workshop Series (Starting March 2026)

## Key Messages
- "Save 20+ hours per week with AI automation"
- "Transform your business operations"
- "From manual to automated in 2 weeks"
```

## Troubleshooting

### LinkedIn Login Required
- Session data may have expired
- Re-run with `--login` flag to re-authenticate
- Consider saving session data for persistence

### Post Not Publishing
- Check if LinkedIn is accessible
- Verify session is still valid
- Review content for formatting issues
- Check for rate limiting (too many posts)

### Content Not Generating
- Ensure `Business_Goals.md` exists with services
- Check `Company_Handbook.md` for brand guidelines
- Verify vault path is correct

## Integration with Orchestrator

The LinkedIn Poster can work with the main `orchestrator.py`:
1. Scheduled task triggers post generation
2. AI creates draft and moves to `Pending_Approval/`
3. Human reviews and approves
4. Orchestrator detects approval and posts
5. Post logged and dashboard updated

## Best Practices

1. **Quality Over Quantity**: Better to post 2 great posts/week than 7 mediocre ones
2. **Engage With Comments**: When people comment, respond promptly
3. **Track Metrics**: Monitor which posts get most engagement
4. **Iterate**: Learn from performance data to improve future posts
5. **Mix Content Types**: Don't just sell - educate, inspire, and engage
6. **Use Visuals**: Posts with images get 2x more engagement
7. **Post Consistently**: Regular posting builds audience expectations

## Next Steps (Gold Tier Enhancements)

- Auto-scheduling based on optimal posting times
- Engagement metric tracking (likes, comments, shares)
- Competitor analysis and trending topic detection
- Multi-platform posting (Twitter, Facebook)
- Image generation for posts
- Comment response suggestions
- Lead tracking from post engagements
