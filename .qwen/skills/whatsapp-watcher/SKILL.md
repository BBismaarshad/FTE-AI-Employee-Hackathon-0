# WhatsApp Watcher Skill

Monitor WhatsApp Web for new messages and create action files for the AI Employee.

## Overview

This skill provides a WhatsApp Watcher that uses Playwright to monitor WhatsApp Web for new messages containing important keywords. It detects urgent messages and creates structured `.md` action files in the vault's `Needs_Action` folder for the AI Employee to process.

## Features

- **WhatsApp Web Automation**: Uses Playwright to interact with WhatsApp Web
- **Keyword Detection**: Monitors for urgent keywords like "urgent", "asap", "invoice", "payment", "help"
- **Session Persistence**: Saves browser session to avoid re-scanning QR code every time
- **Unread Message Detection**: Identifies chats with unread messages
- **Structured Action Files**: Creates well-formatted markdown files with message content
- **Configurable Keywords**: Customizable keyword list for your business needs
- **Restart Persistence**: Tracks processed messages to avoid duplicates

## Prerequisites

1. **Python Dependencies**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **WhatsApp Web Access**:
   - You must be able to access WhatsApp Web
   - First run will require QR code scanning
   - Keep browser session saved for persistence

3. **System Requirements**:
   - Chromium browser (installed via `playwright install chromium`)
   - Graphical environment (or virtual display for servers)

## Installation

1. Ensure all prerequisites are installed
2. Copy `whatsapp_watcher.py` to the `watchers/` directory
3. First run will open WhatsApp Web for QR code scanning
4. Session will be cached for future runs

## Usage

### Continuous Monitoring
```bash
python watchers/whatsapp_watcher.py --vault /path/to/AI_Employee_Vault
```

### Single Check (for testing/scheduled tasks)
```bash
python watchers/whatsapp_watcher.py --vault /path/to/AI_Employee_Vault --once
```

### Custom Keywords
```bash
python watchers/whatsapp_watcher.py --vault /path/to/AI_Employee_Vault --keywords "urgent invoice payment help"
```

### Headless Mode (for servers)
```bash
python watchers/whatsapp_watcher.py --vault /path/to/AI_Employee_Vault --headless
```

## How It Works

1. **Browser Launch**: Opens Chromium with persistent user data directory
2. **WhatsApp Web Navigation**: Navigates to web.whatsapp.com
3. **Session Check**: Waits for successful login (chat list to load)
4. **Unread Detection**: Scans chat list for unread messages
5. **Keyword Matching**: Checks message text against configured keywords
6. **Action File Creation**: Creates `.md` files in `Needs_Action/` with:
   - Chat name/contact
   - Message text preview
   - Matched keywords
   - Suggested action checkboxes
7. **State Persistence**: Saves processed message IDs to `.state/whatsapp_watcher.txt`

## Action File Format

```markdown
---
type: whatsapp_message
from: Contact Name
chat_id: chat_identifier
received: 2026-04-06T10:30:00
priority: high
matched_keywords: urgent, invoice
status: pending
---

## WhatsApp Message

**From**: Contact Name  
**Chat**: chat_identifier  
**Received**: 2026-04-06 10:30:00  
**Priority**: high

## Message Preview
Hey, can you send me the invoice for January? This is urgent.

## Matched Keywords
- urgent
- invoice

## Suggested Actions
- [ ] Read full message in WhatsApp
- [ ] Respond to contact
- [ ] Take requested action
- [ ] Archive after processing

---
*Detected by WhatsApp Watcher at 2026-04-06 10:30:00*
```

## Security Notes

- **WhatsApp Terms of Service**: Be aware of WhatsApp's automation policies
- **Session Security**: Session data is stored locally - protect it
- **Rate Limiting**: Avoid excessive polling to prevent account restrictions
- **Privacy**: Only monitor business-related contacts and messages
- **Headless Mode**: Use with caution - may trigger security checks

## Configuration

### Custom Keywords File
For easier management, you can create a `keywords.txt` file:

```
urgent
asap
invoice
payment
help
deadline
immediately
important
```

Then reference it:
```bash
python watchers/whatsapp_watcher.py --vault /path/to/vault --keywords-file keywords.txt
```

### Check Interval
- **Recommended**: 30-60 seconds for business use
- **Conservative**: 120-300 seconds to avoid rate limiting
- Adjust based on your needs and WhatsApp's behavior

## Troubleshooting

### QR Code Required Every Time
- Session data may have been deleted
- Ensure `--session-path` points to a persistent directory
- Check that the directory has write permissions

### WhatsApp Web Not Loading
- Check internet connection
- Increase `--timeout` value for slower connections
- Try running without `--headless` first to debug

### No Messages Detected
- Verify WhatsApp Web is successfully logged in
- Check if messages contain your configured keywords
- Review keyword matching logic (case-insensitive by default)

### Playwright Errors
- Reinstall Chromium: `playwright install chromium`
- Check Playwright version compatibility
- Ensure no other process is blocking the browser

## Integration with Orchestrator

The WhatsApp Watcher works with the main `orchestrator.py`:
1. Watcher detects messages with keywords
2. Creates action files in `Needs_Action/`
3. Orchestrator detects new action files
4. Orchestrator triggers AI to process them
5. AI creates plans and suggests responses
6. Files move to `Done/` after completion

## Advanced Usage

### Multiple Keyword Sets
You can run multiple watchers with different keyword sets:
```bash
# Urgent business messages
python whatsapp_watcher.py --vault /path/to/vault --keywords "urgent invoice payment"

# Customer support
python whatsapp_watcher.py --vault /path/to/vault --keywords "help support issue bug"
```

### Message Response Templates
Create response templates in your vault:
```
/Vault/Templates/WhatsApp/
  - invoice_request.md
  - payment_confirmation.md
  - meeting_reminder.md
```

## Next Steps (Gold Tier Enhancements)

- Full message history retrieval
- Media/message attachment handling
- Auto-reply suggestions
- Contact management and grouping
- Message sentiment analysis
- WhatsApp Business API integration (official API)
