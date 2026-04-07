# LinkedIn Auto-Poster Skill

Automatically generate and post professional content to LinkedIn for business promotion.

## Overview

The LinkedIn Auto-Poster creates professional LinkedIn posts based on your business goals and can automatically publish them after human approval. It includes:

- **5 content categories** with multiple templates each
- **Human-in-the-loop approval workflow**
- **Draft generation** for review before posting
- **Automated posting** via Playwright browser automation
- **Logging** of all posts and results

**Warning**: Automated LinkedIn posting may violate LinkedIn's Terms of Service. Always review AI-generated content before publishing and consider using the official LinkedIn API for production.

## Content Categories

### 1. Service Announcement
Promote new services or offerings with benefits and features.

### 2. Success Story
Share client success stories with measurable results.

### 3. Industry Insight
Provide valuable tips and industry insights.

### 4. Behind the Scenes
Show your work process and projects.

### 5. Thought Leadership
Share opinions and insights to establish authority.

## Usage

### Generate a Draft

```bash
python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate
```

This creates a draft post in `AI_Employee_Vault/Drafts/LinkedIn/`.

### Generate with Approval Workflow

```bash
python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post
```

This:
1. Generates a post
2. Creates a draft file
3. Creates an approval request in `Pending_Approval/LinkedIn/`
4. Waits for human approval

### Generate Specific Category

```bash
python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate --category success_story
```

Available categories:
- `service_announcement`
- `success_story`
- `industry_insight`
- `behind_the_scenes`
- `thought_leadership`

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--vault` | Path to Obsidian vault | Required |
| `--generate` | Generate draft only | False |
| `--post` | Generate with approval workflow | False |
| `--category` | Specific post category | Random |
| `--session-path` | Path to LinkedIn browser session | `./credentials/linkedin_session/` |
| `--headless` | Run browser in headless mode | False |

## Workflow

### Draft-Only Workflow (Safe)

1. **Generate Draft**: Run with `--generate`
2. **Review**: Check the draft in `Drafts/LinkedIn/`
3. **Edit**: Modify the content if needed
4. **Move**: Copy to `Needs_Action/` when ready

### Approval Workflow (Recommended)

1. **Generate**: Run with `--post`
2. **Draft Created**: Saved to `Drafts/LinkedIn/`
3. **Approval Request**: Created in `Pending_Approval/LinkedIn/`
4. **Human Review**: Review and edit the draft
5. **Approve**: Move approval file to `Approved/LinkedIn/`
6. **Auto-Post**: Orchestrator posts via Playwright
7. **Log**: Post recorded in logs

### Automated Posting (Use with Caution)

For fully automated posting (bypasses manual review):

1. Approval file moved to `Approved/`
2. Orchestrator detects approved post
3. Playwright opens LinkedIn
4. Post is published automatically
5. Result logged to `Logs/linkedin_posts.json`

## Content Templates

The poster uses smart templates that fill in content based on your business goals. Templates include:

### Service Announcement Example

```
🚀 Excited to announce our new AI Automation Consulting service!

We help businesses save 20+ hours per week with cutting-edge AI and automation solutions.

✅ Reduce manual work by 85%
✅ Cut errors by 95%
✅ Save thousands in operational costs

DM me to learn how we can transform your workflow.

#BusinessGrowth #Innovation #TechSolutions
```

### Success Story Example

```
📊 Client Success Story:

A local business was spending 15 hours/week on manual data entry.

We implemented a solution that:
✅ Reduced processing time by 85%
✅ Cut errors by 95%
✅ Saved $3,000/month in labor costs

The result? They can now focus on growing their business instead of managing spreadsheets.

#CaseStudy #Results #BusinessGrowth
```

## Customization

### Edit Business Goals

The poster reads `Business_Goals.md` to guide content generation. Update this file with:

```markdown
# Business Goals

## Active Projects
- AI Automation Consulting
- Workflow Optimization Services
- Custom Integration Solutions

## Key Messages
- Transform your business with AI
- Save time and reduce errors
- Scale efficiently
```

### Add Custom Templates

Edit `skills/linkedin_poster.py` and add to the `TEMPLATES` dict:

```python
TEMPLATES = {
    'my_custom_category': [
        {
            'text': """Your template with {placeholders}""",
            'hashtags': ['#Your', '#Hashtags']
        }
    ]
}
```

## Troubleshooting

### "Playwright is required"
- Install Playwright: `pip install playwright`
- Install browser: `playwright install chromium`

### Post not appearing on LinkedIn
- Check that you're logged in to LinkedIn
- LinkedIn UI may have changed - update selectors in code
- Run without `--headless` to debug

### Login required
- First run requires manual login
- Run poster once without `--headless`
- Session will be saved

### Content seems generic
- Update `Business_Goals.md` with specific services
- Add more details to your business objectives
- Manually edit generated drafts

### Rate limiting or warnings from LinkedIn
- **STOP** posting immediately
- LinkedIn may flag automated content
- Reduce posting frequency
- Consider official LinkedIn API

## Best Practices

### Content Review
- **Always** review AI-generated content before posting
- Ensure accuracy of claims and statistics
- Match your personal voice and style
- Check for any sensitive information

### Posting Frequency
- Don't post more than 1-2 times per day
- Space posts throughout the week
- Monitor engagement metrics
- Adjust based on audience response

### Compliance
- Disclose AI assistance when appropriate
- Follow LinkedIn's content guidelines
- Respect copyright and attribution
- Maintain professional standards

## Integration with Orchestrator

The LinkedIn Auto-Poster works with the approval system:

1. Poster creates draft and approval request
2. Human reviews and approves
3. Orchestrator detects approved file
4. Post is published via Playwright
5. Result logged and file moved to `Done/`

## Next Steps

- Set up scheduled post generation via Task Scheduler
- Integrate with Gmail Watcher for lead responses
- Add Facebook/Instagram posting (Gold tier)
- Track engagement metrics
