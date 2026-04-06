# Email MCP Server Skill

Send emails and manage email operations via Model Context Protocol (MCP).

## Overview

This skill provides an MCP server that enables your AI Employee to send emails, create drafts, and manage email operations. It integrates with Gmail API and works with the Human-in-the-Loop approval workflow.

## Features

- **Email Sending**: Send emails via Gmail API
- **Draft Creation**: Create email drafts for review
- **Template Support**: Use predefined email templates
- **Attachment Handling**: Attach files from vault
- **Approval Integration**: Works with HITL workflow
- **Audit Logging**: All email actions logged
- **Rate Limiting**: Prevents email spam

## Prerequisites

1. **Python Dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Gmail API Credentials**:
   - Same credentials as Gmail Watcher
   - Requires send scope: `https://www.googleapis.com/auth/gmail.send`

3. **MCP Framework**:
   ```bash
   pip install mcp
   ```

## Installation

1. Ensure all prerequisites are installed
2. Copy `email_mcp_server.py` to project root
3. Update credentials path in configuration
4. Register MCP server in Claude Code config

## Usage

### Standalone Server
```bash
python skills/email_mcp_server.py --credentials /path/to/credentials.json
```

### Via Claude Code MCP Config

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/path/to/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

## MCP Tools Provided

### 1. `send_email`
Send an email to a recipient.

**Parameters**:
- `to` (string): Recipient email address
- `subject` (string): Email subject
- `body` (string): Email body text
- `html` (string, optional): HTML version of email
- `attachment_path` (string, optional): Path to file attachment

**Example**:
```python
# Tool call
{
  "name": "send_email",
  "arguments": {
    "to": "client@example.com",
    "subject": "Invoice #1234 - January 2026",
    "body": "Dear Client,\n\nPlease find attached your invoice for January 2026.\n\nBest regards,\nYour Company",
    "attachment_path": "/path/to/invoice.pdf"
  }
}

# Response
{
  "success": true,
  "message_id": "msg_abc123",
  "sent_at": "2026-04-06T10:30:00Z"
}
```

### 2. `create_draft`
Create an email draft for review (doesn't send).

**Parameters**:
- `to` (string): Recipient email address
- `subject` (string): Email subject
- `body` (string): Email body text
- `attachment_path` (string, optional): Path to attachment

**Example**:
```python
# Response
{
  "success": true,
  "draft_id": "draft_xyz789",
  "message": "Draft created successfully"
}
```

### 3. `list_recent_emails`
List recently sent emails (for context).

**Parameters**:
- `limit` (int, default=10): Number of emails to return
- `days` (int, default=7): Look back this many days

**Example**:
```python
# Response
{
  "emails": [
    {
      "to": "client@example.com",
      "subject": "Invoice #1234",
      "sent_at": "2026-04-05T14:20:00Z"
    }
  ]
}
```

### 4. `validate_email`
Validate an email address format.

**Parameters**:
- `email` (string): Email address to validate

**Example**:
```python
# Response
{
  "valid": true,
  "email": "client@example.com"
}
```

## Security Features

### 1. Approval Required
For sensitive emails, use the approval workflow:
- New recipients require approval
- Bulk sends require approval
- Emails with attachments over threshold need review

### 2. Rate Limiting
Prevents accidental spam:
- Max 10 emails per hour (configurable)
- Max 50 emails per day
- Cooldown between sends (30 seconds)

### 3. Dry Run Mode
Test email operations without sending:
```bash
export DRY_RUN=true
```

### 4. Allowlist/Blocklist
Configure allowed recipients:
```json
{
  "allowlist": ["trusted@example.com", "partner@company.com"],
  "blocklist": ["spam@bad.com"]
}
```

## Approval Workflow Integration

When email sending requires approval:

1. **AI Detects Sensitive Action**: New recipient, large attachment, etc.
2. **Creates Approval File**: In `/Pending_Approval/`
3. **Human Reviews**: Checks email content and details
4. **Approves**: Moves file to `/Approved/`
5. **MCP Sends Email**: Orchestrator triggers actual send
6. **Logs Result**: Email send logged with approval status

### Approval File Format

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #1234 - January 2026
attachment: /Vault/Invoices/2026-04_Client.pdf
created: 2026-04-06T10:30:00Z
status: pending
---

# Email Approval Required

## Details
- **To**: client@example.com
- **Subject**: Invoice #1234 - January 2026
- **Attachment**: 2026-04_Client.pdf (245 KB)
- **Body Preview**: "Dear Client, Please find attached your invoice..."

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Email sending requires human approval*
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Auth Failed | Credentials expired | Re-authenticate |
| Rate Limited | Too many sends | Wait for cooldown |
| Invalid Recipient | Bad email format | Fix and retry |
| Attachment Not Found | File path wrong | Verify path |
| Quota Exceeded | Gmail API limit | Wait or increase quota |

## Configuration

### Environment Variables
```env
GMAIL_CREDENTIALS=/path/to/credentials.json
GMAIL_TOKEN=/path/to/token.json
DRY_RUN=false
MAX_EMAILS_PER_HOUR=10
MAX_EMAILS_PER_DAY=50
SEND_COOLDOWN_SECONDS=30
```

### MCP Server Options
```bash
python email_mcp_server.py \
  --credentials /path/to/creds.json \
  --max-per-hour 10 \
  --max-per-day 50 \
  --cooldown 30 \
  --dry-run
```

## Logging

All email operations logged to:
- `/Vault/Logs/email_operations.json`

Log format:
```json
{
  "timestamp": "2026-04-06T10:30:00Z",
  "action": "send_email",
  "to": "client@example.com",
  "subject": "Invoice #1234",
  "result": "success",
  "message_id": "msg_abc123",
  "approval_status": "approved",
  "approved_by": "human"
}
```

## Troubleshooting

### Authentication Errors
- Delete token file and re-authenticate
- Ensure Gmail API is enabled
- Check credentials file path

### Rate Limiting
- Check `email_operations.json` for send history
- Increase limits if needed
- Implement proper cooldown

### Email Not Sending
- Check if in dry run mode
- Verify recipient not blocked
- Review error logs

## Best Practices

1. **Always Use Approval for New Recipients**: Never auto-send to unknown addresses
2. **Log Everything**: Maintain complete audit trail
3. **Test with Dry Run First**: Verify emails before actual sending
4. **Monitor Rate Limits**: Track sends to avoid hitting limits
5. **Use Templates**: Consistent email formatting
6. **Review Before Sending**: Even approved emails should be spot-checked

## Next Steps (Gold Tier Enhancements)

- Email threading and reply management
- Template library with variable substitution
- Scheduled email sending
- Email response tracking
- Multi-account support (personal + business)
- HTML email templates
- Unsubscribe management
