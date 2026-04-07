# Email MCP Server Skill

Send emails and create drafts via Gmail API with rate limiting and audit logging.

## Overview

The Email MCP (Model Context Protocol) Server provides the AI Employee with the ability to:
- **Send emails** via Gmail API
- **Create drafts** for review
- **List recent emails** sent
- **Rate limit** outgoing messages
- **Audit log** all email operations
- **Dry-run mode** for testing

This is one of the "hands" of your AI Employee - it can take action by sending emails.

## Security Features

### Rate Limiting
- **Cooldown period**: 30 seconds between emails (configurable)
- **Hourly limit**: 10 emails per hour (configurable)
- **Daily limit**: 50 emails per day (configurable)

### Dry-Run Mode
Test the email workflow without actually sending messages.

### Audit Logging
All email operations are logged with timestamps for compliance.

### Approval Workflow
Sensitive emails should go through the human-in-the-loop approval system.

## Setup Instructions

### 1. Gmail API Credentials

The Email MCP Server uses the same credentials as the Gmail Watcher:

1. Ensure `credentials.json` is in the project root
2. The token file will be auto-created on first run
3. Gmail API scopes needed:
   - `gmail.send`
   - `gmail.compose`
   - `gmail.readonly`

### 2. First Run Authentication

```bash
python skills/email_mcp_server.py --credentials ./credentials/gmail_credentials.json
```

This will:
- Open a browser for OAuth
- Request permission to send emails
- Save token for future use

## Usage

### Interactive Mode

```bash
python skills/email_mcp_server.py --credentials ./credentials/gmail_credentials.json
```

Available commands:
```
send <to@email.com> <Subject> <Body>
draft <to@email.com> <Subject> <Body>
list [limit]
quit
```

### Dry-Run Mode (Testing)

```bash
python skills/email_mcp_server.py --credentials ./credentials/gmail_credentials.json --dry-run
```

This logs what would be sent without actually sending.

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--credentials` | Path to Gmail credentials | `./credentials.json` |
| `--token` | Path to token file | Auto-detected |
| `--vault` | Path to vault for logging | `./AI_Employee_Vault` |
| `--dry-run` | Don't actually send emails | False |
| `--max-per-hour` | Max emails per hour | 10 |
| `--max-per-day` | Max emails per day | 50 |
| `--cooldown` | Cooldown between sends (seconds) | 30 |

## Integration with AI Employee

### Approval Workflow

When the AI Employee needs to send an email:

1. **AI creates draft** in `Pending_Approval/Email/`
2. **Human reviews** the draft
3. **Human approves** by moving to `Approved/Email/`
4. **Orchestrator sends** via Email MCP Server
5. **Email logged** and action moved to `Done/`

### Example Approval File

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Project Update - April 2026
created: 2026-04-06T10:30:00
status: pending
---

# Email Approval Required

## Recipient
client@example.com

## Subject
Project Update - April 2026

## Body
Dear Client,

I'm writing to provide an update on our project...

[Full email content]

---
Move this file to Approved/ to send, or Rejected/ to cancel.
```

## Rate Limiting Details

### Why Rate Limits?
- Prevents accidental spam
- Protects your Gmail reputation
- Avoids Google account suspension
- Ensures thoughtful communication

### Default Limits
- **10 emails/hour**: Allows focused communication
- **50 emails/day**: Reasonable daily volume
- **30s cooldown**: Time to review between sends

### Adjusting Limits

For higher volumes, increase limits cautiously:

```bash
python skills/email_mcp_server.py \
  --credentials ./credentials/gmail_credentials.json \
  --max-per-hour 20 \
  --max-per-day 100 \
  --cooldown 15
```

**Warning**: Gmail may flag unusually high sending activity.

## Audit Logs

All email operations are logged to:
```
AI_Employee_Vault/Logs/email_operations.json
```

Log format:
```json
{
  "timestamp": "2026-04-06T10:30:00",
  "action": "send_email",
  "to": "client@example.com",
  "subject": "Project Update",
  "message_id": "msg_123abc",
  "result": "success"
}
```

## Troubleshooting

### "Invalid email address"
- Check email format (e.g., user@domain.com)
- Ensure no extra spaces or characters

### "Rate limit exceeded"
- Wait for cooldown period (30s)
- Check hourly/daily limits
- Reduce sending frequency

### "Authentication error"
- Delete token file and re-authenticate
- Ensure Gmail API is enabled
- Check credentials file

### "Gmail API error: Quota exceeded"
- You've hit Google's API quota
- Wait for quota to reset (typically daily)
- Request quota increase in Google Cloud Console

### Emails not being received
- Check recipient spam folder
- Verify email address is correct
- Check Gmail sending limits

## Best Practices

### Email Content
- Keep emails professional and concise
- Include clear subject lines
- Use proper formatting
- Add signatures if needed

### Sending Practices
- Review all emails before sending
- Use drafts for important messages
- Respect rate limits
- Monitor audit logs

### Compliance
- Follow email marketing regulations
- Honor unsubscribe requests
- Maintain professional standards
- Keep records of business communications

## Integration Points

### Gmail Watcher
- Gmail Watcher **reads** incoming emails
- Email MCP Server **sends** replies
- Together they form a complete email workflow

### Orchestrator
- Orchestrator triggers Email MCP Server
- Monitors approval folders
- Logs all actions

### Qwen Code
- Qwen Code drafts email content
- Suggests appropriate responses
- Creates approval files

## Next Steps

- Set up email templates for common responses
- Integrate with calendar for scheduling
- Add attachment support
- Create email analytics dashboard
