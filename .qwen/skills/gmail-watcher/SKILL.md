# Gmail Watcher Skill

Monitor Gmail for unread/important emails and create action files for the AI Employee.

## Overview

The Gmail Watcher is one of the "senses" of your AI Employee. It continuously monitors your Gmail account for unread messages and creates structured action files in the `Needs_Action` folder for the orchestrator to process.

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API**:
   - Navigate to **APIs & Services** > **Library**
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Navigate to **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **OAuth client ID**
   - Select **Desktop app** as the application type
   - Give it a name like "AI Employee Gmail"
   - Download the credentials JSON file

### 2. Credentials Setup

1. Place the downloaded credentials JSON file in the project root as `credentials.json`
2. The file should already be in this directory as `credentials/gmail_credentials.json`

### 3. First Run Authentication

Run the Gmail Watcher for the first time:

```bash
python watchers/gmail_watcher.py --vault ./AI_Employee_Vault --credentials ./credentials/gmail_credentials.json --once
```

This will:
- Open a browser window
- Ask you to sign in with your Google account
- Request permission to read your emails
- Save a token file for future use

**Important**: The token is saved in `credentials/token.json` and will be reused for subsequent runs.

## Usage

### Run Once (for testing or scheduled tasks)

```bash
python watchers/gmail_watcher.py --vault ./AI_Employee_Vault --once
```

### Run Continuously

```bash
python watchers/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120
```

This checks for new emails every 2 minutes.

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--vault` | Path to Obsidian vault | Required |
| `--credentials` | Path to Gmail credentials JSON | `./credentials/gmail_credentials.json` |
| `--token` | Path to store token | `./credentials/token.json` |
| `--interval` | Check interval in seconds | 120 |
| `--once` | Run once and exit | False |
| `--mark-read` | Mark emails as read after processing | False |

## How It Works

1. **Authentication**: Loads OAuth token or prompts for login
2. **Check for Updates**: Queries Gmail for unread messages
3. **Filter**: Excludes already-processed emails
4. **Create Action Files**: For each new email, creates a `.md` file in `Needs_Action/`
5. **Track**: Saves processed email IDs to avoid duplicates

## Action File Format

Each detected email creates an action file like this:

```markdown
---
type: email
from: sender@example.com
subject: Meeting Request
received: 2026-04-06T10:30:00
priority: high
status: pending
---

# Email: Meeting Request

## Metadata
- **From**: John Doe <john@example.com>
- **Received**: Mon, 6 Apr 2026 10:30:00 +0000
- **Priority**: high

## Preview
Can we schedule a meeting for tomorrow?

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply if action required
- [ ] Forward to relevant person/team
- [ ] Archive after processing
```

## Priority Detection

- **High**: Emails marked as "IMPORTANT" by Gmail
- **Normal**: Regular unread emails
- **Low**: Promotions/category emails

## Troubleshooting

### "Gmail credentials file not found"
- Ensure `credentials.json` exists in the project root
- Or specify the path with `--credentials`

### "Token expired" or authentication errors
- Delete `credentials/token.json` and re-run
- The watcher will prompt for re-authentication

### No emails detected
- Check that emails are actually unread
- Verify the correct Gmail account is being monitored
- Check API quotas in Google Cloud Console

### Rate limiting errors
- Gmail API has quotas; reduce `--interval` if hitting limits
- Check Google Cloud Console for quota details

## Integration with Orchestrator

The Gmail Watcher works with the orchestrator:

1. Watcher creates action files in `Needs_Action/`
2. Orchestrator detects new files and creates plans
3. Qwen Code processes the plans and suggests actions
4. Completed actions move to `Done/`

## Next Steps

- Set up Windows Task Scheduler to run the watcher every 2 minutes
- Integrate with Email MCP Server to send replies
- Add filtering rules in Company_Handbook.md
