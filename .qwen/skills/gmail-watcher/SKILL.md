# Gmail Watcher Skill

Monitor Gmail for unread/important emails and create action files for the AI Employee.

## Overview

This skill provides a Gmail Watcher that continuously monitors your Gmail account for new unread messages, extracts email metadata and content, and creates structured `.md` action files in the vault's `Needs_Action` folder for the AI Employee to process.

## Features

- **OAuth 2.0 Authentication**: Secure Gmail API access using Google OAuth credentials
- **Unread Email Detection**: Monitors for unread and important emails
- **Duplicate Prevention**: Tracks processed emails to avoid creating duplicate action files
- **Structured Action Files**: Creates well-formatted markdown files with email metadata
- **Priority Detection**: Identifies high-priority emails based on sender and subject
- **Restart Persistence**: Remembers processed emails across restarts
- **Configurable Intervals**: Adjustable check frequency (default: 120 seconds)

## Prerequisites

1. **Google Cloud Project Setup**:
   - Create a Google Cloud Platform project
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download the credentials JSON file

2. **Python Dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. **Environment Variables**:
   Create a `.env` file in the project root (NEVER commit this):
   ```env
   GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
   GMAIL_TOKEN_PATH=/path/to/token.json
   ```

## Installation

1. Ensure all prerequisites are installed
2. Copy `gmail_watcher.py` to the `watchers/` directory
3. Set up Google Cloud credentials (see Prerequisites)
4. First run will open a browser for OAuth authorization
5. Token will be cached for future runs

## Usage

### Continuous Monitoring
```bash
python watchers/gmail_watcher.py --vault /path/to/AI_Employee_Vault
```

### Single Check (for testing/scheduled tasks)
```bash
python watchers/gmail_watcher.py --vault /path/to/AI_Employee_Vault --once
```

### Custom Check Interval
```bash
python watchers/gmail_watcher.py --vault /path/to/AI_Employee_Vault --interval 60
```

## How It Works

1. **Authentication**: Loads OAuth credentials, opens browser for first-time authorization
2. **Polling**: Checks Gmail API every N seconds for unread messages
3. **Filtering**: Skips already-processed emails using message ID tracking
4. **Action File Creation**: Creates `.md` files in `Needs_Action/` with:
   - Email metadata (from, to, subject, date, priority)
   - Email snippet/content
   - Suggested action checkboxes
5. **State Persistence**: Saves processed email IDs to `.state/gmail_watcher.txt`

## Action File Format

```markdown
---
type: email
from: sender@example.com
subject: Email Subject Here
received: 2026-04-06T10:30:00
message_id: abc123def456
priority: high
status: pending
---

## Email Content
Email snippet or preview text...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Security Notes

- **NEVER** commit credentials or token files to version control
- Add `token.json` and credentials files to `.gitignore`
- Store credentials securely using OS keychain when possible
- Use environment variables for file paths
- The watcher only reads emails, never sends them (use Email MCP for sending)

## Troubleshooting

### OAuth Error
- Delete `token.json` and re-run to re-authorize
- Ensure Gmail API is enabled in Google Cloud Console

### No Emails Detected
- Check if emails are already marked as read
- Verify the OAuth token has proper permissions
- Check Gmail filters that might be auto-archiving emails

### API Quota Exceeded
- Increase the `--interval` value to reduce API calls
- Check Google Cloud Console for quota limits

## Integration with Orchestrator

The Gmail Watcher works with the main `orchestrator.py`:
1. Watcher creates action files in `Needs_Action/`
2. Orchestrator detects new action files
3. Orchestrator triggers AI to process them
4. AI creates plans and suggests actions
5. Files move to `Done/` after completion

## Next Steps (Gold Tier Enhancements)

- Full email body extraction (not just snippets)
- Attachment detection and handling
- Email reply via Email MCP
- Label management (auto-archive, flag, etc.)
- Priority scoring based on sender/subject keywords
