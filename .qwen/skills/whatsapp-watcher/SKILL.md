# WhatsApp Watcher Skill

Monitor WhatsApp Web for urgent messages and keyword-based alerts.

## Overview

The WhatsApp Watcher uses Playwright (browser automation) to monitor WhatsApp Web for:
- Messages containing urgent keywords
- Unread conversations
- Important requests requiring attention

**Warning**: Automated WhatsApp access may violate WhatsApp's Terms of Service. Use at your own risk. Consider using WhatsApp Business API for production.

## Setup Instructions

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. First Run - QR Code Scan

The first time you run the WhatsApp Watcher:

1. Run the watcher:
   ```bash
   python watchers/whatsapp_watcher.py --vault ./AI_Employee_Vault --once
   ```

2. A browser window will open showing a **QR code**

3. **Scan the QR code** with your WhatsApp mobile app:
   - Open WhatsApp on your phone
   - Go to Settings/Menu > Linked Devices
   - Tap "Link a Device"
   - Point your camera at the QR code

4. Your WhatsApp session will be saved for future runs

### 3. Session Persistence

After successful login, the browser session is saved to:
```
credentials/whatsapp_session/
```

You won't need to scan the QR code again unless the session expires.

## Usage

### Run Once (Testing)

```bash
python watchers/whatsapp_watcher.py --vault ./AI_Employee_Vault --once
```

### Run Continuously

```bash
python watchers/whatsapp_watcher.py --vault ./AI_Employee_Vault --interval 30
```

This checks WhatsApp every 30 seconds.

### Custom Keywords

```bash
python watchers/whatsapp_watcher.py \
  --vault ./AI_Employee_Vault \
  --keywords urgent invoice payment deadline ASAP \
  --once
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--vault` | Path to Obsidian vault | Required |
| `--session-path` | Path to store browser session | `./credentials/whatsapp_session/` |
| `--keywords` | Keywords to monitor | `urgent asap invoice payment help` |
| `--interval` | Check interval in seconds | 30 |
| `--once` | Run once and exit | False |
| `--headless` | Run browser without UI | False |
| `--timeout` | Browser timeout in ms | 30000 |

## How It Works

1. **Browser Launch**: Opens Chromium with persistent session
2. **WhatsApp Web Load**: Navigates to web.whatsapp.com
3. **Login Check**: Waits for QR scan or uses saved session
4. **Unread Detection**: Finds chats with unread messages
5. **Keyword Matching**: Only flags messages with urgent keywords
6. **Action Files**: Creates `.md` files in `Needs_Action/`

## Default Keywords

- `urgent`
- `asap`
- `invoice`
- `payment`
- `help`

### High Priority Keywords

Messages containing these are marked as **high priority**:
- `urgent`
- `asap`
- `immediately`
- `emergency`

## Customization

### Add Your Own Keywords

Edit `watchers/whatsapp_watcher.py`:

```python
self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help',
                 'deadline', 'meeting', 'contract', 'review']
```

### Adjust Check Interval

For less frequent checking:
```bash
python watchers/whatsapp_watcher.py --vault ./AI_Employee_Vault --interval 60
```

## Troubleshooting

### "QR code detected" message
- This is normal on first run
- Scan the QR code with your phone
- Session will be saved

### Session expired
- Run the watcher again
- You may need to re-scan QR code
- Sessions typically last 30-90 days

### No messages detected
- Ensure you have unread messages
- Check that keywords match your messages
- Run without `--headless` to see browser

### Browser opens but WhatsApp doesn't load
- Check internet connection
- WhatsApp Web may be temporarily unavailable
- Try again in a few minutes

### WhatsApp Web keeps logging out
- Session folder may be corrupted
- Delete `credentials/whatsapp_session/` and re-scan
- Avoid using WhatsApp Web on other devices simultaneously

## Security Considerations

### Session Data
- Browser session contains your WhatsApp cookies
- **Never** share the `credentials/whatsapp_session/` folder
- Protect this folder from unauthorized access

### Privacy
- All message content is saved to action files
- Ensure your vault is secure
- Be aware of data retention policies

### Terms of Service
- WhatsApp Web automation may violate ToS
- Use at your own risk
- Consider WhatsApp Business API for production

## Best Practices

### Keyword Selection
- Keep keywords specific to your needs
- Avoid too many false positives
- Update based on actual message patterns

### Checking Frequency
- 30 seconds: Real-time monitoring
- 60 seconds: Balanced approach
- 300 seconds: Casual monitoring

### Action File Management
- Review action files regularly
- Move processed files to `Done/`
- Archive important conversations

## Integration with Orchestrator

The WhatsApp Watcher works with the orchestrator:

1. Watcher detects keyword messages
2. Creates action files in `Needs_Action/`
3. Orchestrator processes and creates plans
4. Qwen Code suggests responses
5. Completed actions move to `Done/`

## Next Steps

- Set up Windows Task Scheduler for automated monitoring
- Add custom response templates
- Integrate with email for comprehensive communication monitoring
- Consider WhatsApp Business API for production use
