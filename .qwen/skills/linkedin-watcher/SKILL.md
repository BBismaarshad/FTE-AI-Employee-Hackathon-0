# LinkedIn Watcher Skill

Monitor LinkedIn for messages, connection requests, and notifications.

## Overview

The LinkedIn Watcher uses Playwright (headless browser automation) to monitor LinkedIn for:
- New messages containing important keywords
- Connection requests
- Job opportunities
- Post engagement notifications

**Warning**: Automated LinkedIn access may violate LinkedIn's Terms of Service. Use at your own risk and consider using the official LinkedIn API for production use.

## Setup Instructions

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. First Run - Manual Login

The first time you run the LinkedIn Watcher, it will open a browser window where you need to:

1. **Log in to LinkedIn** with your credentials
2. **Complete any CAPTCHA** if prompted
3. The session will be saved for future runs

Run the watcher:

```bash
python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault --once
```

### 3. Session Persistence

After successful login, the browser session is saved to:
```
credentials/linkedin_session/
```

This session persists across restarts, so you won't need to log in again unless:
- LinkedIn forces re-authentication
- Session expires (typically after 30-90 days)
- You clear the session folder

## Usage

### Run Once (for testing)

```bash
python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault --once
```

### Run Continuously

```bash
python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault --interval 300
```

This checks LinkedIn every 5 minutes (300 seconds).

### Run with Visible Browser (for debugging)

```bash
python watchers/linkedin_watcher.py --vault ./AI_Employee_Vault --once
```

Omit `--headless` to see the browser window.

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--vault` | Path to Obsidian vault | Required |
| `--session-path` | Path to store browser session | `./credentials/linkedin_session/` |
| `--interval` | Check interval in seconds | 300 (5 min) |
| `--once` | Run once and exit | False |
| `--headless` | Run browser without UI | False |
| `--timeout` | Browser timeout in ms | 30000 |

## How It Works

1. **Browser Initialization**: Launches Chromium with persistent session
2. **LinkedIn Login**: Waits for you to log in (first run only)
3. **Check Messages**: Scans messaging inbox for unread/conversations
4. **Check Notifications**: Monitors notifications for connections/opportunities
5. **Keyword Matching**: Only flags messages containing keywords like:
   - opportunity
   - project
   - collaboration
   - invoice
   - payment
   - urgent
   - partnership
   - consulting
6. **Create Action Files**: Generates `.md` files in `Needs_Action/`

## Action File Format

### Message Action File

```markdown
---
type: linkedin_message
from: John Doe
received: 2026-04-06T10:30:00
priority: high
linkedin_url: https://www.linkedin.com/messaging/
status: pending
---

# LinkedIn Message

## Metadata
- **Type**: linkedin_message
- **From**: John Doe
- **Received**: 2026-04-06T10:30:00
- **Priority**: high
- **LinkedIn URL**: https://www.linkedin.com/messaging/

## Message Content
Hi, I'd like to discuss a collaboration opportunity...

## Matched Keywords
opportunity, collaboration

## Suggested Actions
- [ ] Read full conversation on LinkedIn
- [ ] Respond to message
- [ ] Check if action required
- [ ] Archive after processing
```

### Notification Action File

```markdown
---
type: linkedin_notification_opportunity
from: LinkedIn
received: 2026-04-06T10:30:00
priority: high
linkedin_url: https://www.linkedin.com/notifications/
status: pending
---

# LinkedIn Notification

## Metadata
- **Type**: linkedin_notification_opportunity
- **From**: LinkedIn
- **Received**: 2026-04-06T10:30:00
- **Priority**: high
- **LinkedIn URL**: https://www.linkedin.com/notifications/

## Notification Content
A job opportunity matching your profile...

## Category
opportunity

## Suggested Actions
- [ ] Review notification on LinkedIn
- [ ] Take appropriate action if needed
- [ ] Archive after processing
```

## Keyword Customization

Edit the `keywords` list in `watchers/linkedin_watcher.py`:

```python
self.keywords = ['opportunity', 'project', 'collaboration', 'invoice',
                'payment', 'urgent', 'partnership', 'consulting']
```

## Troubleshooting

### "LinkedIn login required"
- Run the watcher without `--headless` to see the browser
- Log in manually when prompted
- Session will be saved for future runs

### Browser opens but LinkedIn doesn't load
- Check your internet connection
- LinkedIn may be blocking automated access
- Try running with `--headless` flag removed to debug

### No messages found
- Ensure you're logged in to LinkedIn
- Check that you actually have unread messages
- LinkedIn may have changed their UI selectors (update watcher if needed)

### Session expires frequently
- LinkedIn may require more frequent re-authentication
- Consider using the official LinkedIn API instead

### Rate limiting or account warnings
- **STOP** using the watcher immediately
- LinkedIn may flag your account for automated access
- Consider switching to official API

## Security Considerations

### Session Data
- Browser session contains your login cookies
- Protect the `credentials/linkedin_session/` folder
- Never commit this folder to version control

### Terms of Service
- Automated access may violate LinkedIn's ToS
- Use at your own risk
- Consider official LinkedIn API for production

### Headless Mode
- Running with `--headless` hides the browser window
- Useful for scheduled tasks
- Harder to debug login issues

## Integration with Orchestrator

The LinkedIn Watcher works with the orchestrator:

1. Watcher detects new messages/notifications
2. Creates action files in `Needs_Action/`
3. Orchestrator processes files and creates plans
4. Qwen Code suggests responses or actions
5. Completed actions move to `Done/`

## Next Steps

- Set up Windows Task Scheduler for automated monitoring
- Integrate with LinkedIn Auto-Poster for content publishing
- Add custom keyword filters for your use case
- Consider official LinkedIn API for production use
