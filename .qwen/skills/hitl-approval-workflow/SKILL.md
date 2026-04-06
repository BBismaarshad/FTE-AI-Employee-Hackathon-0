# Human-in-the-Loop (HITL) Approval Workflow

Manage approval requests for sensitive AI Employee actions.

## Overview

This skill provides a file-based approval workflow system that ensures human oversight for sensitive AI Employee actions. Instead of the AI taking actions directly, it creates approval request files that humans can review and approve/reject by moving files between folders.

## Features

- **File-Based Approval**: Simple, auditable approval via file movement
- **Multiple Action Types**: Supports email, payments, social posts, file operations
- **Expiry Handling**: Approval requests expire after configurable time
- **Approval Categories**: Auto-approve, require-approval, always-block
- **Audit Trail**: All approvals/rejections logged
- **Dashboard Integration**: Pending approvals shown in Dashboard.md

## Folder Structure

```
/Vault/
  Pending_Approval/
    - EMAIL_invoice_client.md
    - PAYMENT_vendor_abc.md
    - SOCIAL_post_campaign.md
  Approved/
    - EMAIL_invoice_client.md (moved here when approved)
  Rejected/
    - SOCIAL_post_campaign.md (moved here when rejected)
```

## Approval Categories

### Auto-Approve (No HITL Required)
- Replies to known contacts
- Routine status updates
- File reads/creates
- Scheduled posts already approved

### Require Approval (Default)
- Emails to new recipients
- Payments to any recipient
- Social media posts (first time)
- File deletions
- External API calls

### Always Block (Never Auto-Approve)
- Payments over threshold ($100+)
- Bulk email sends (>10 recipients)
- Subscription cancellations
- Irreversible actions

## Approval File Format

```markdown
---
type: approval_request
action: send_email
to: client@company.com
subject: Invoice #1234 - January 2026
created: 2026-04-06T10:30:00Z
expires: 2026-04-07T10:30:00Z
status: pending
priority: high
action_type: email
---

# Approval Request: Send Email

## Action Details
- **Action Type**: Send Email
- **To**: client@company.com
- **Subject**: Invoice #1234 - January 2026
- **Attachment**: invoice_january.pdf (245 KB)
- **Priority**: High

## Context
Client requested invoice for January consulting services.
This is a known client with established relationship.

## Email Body
Dear Client,

Please find attached your invoice for January 2026 consulting services.

Amount: $1,500
Due Date: February 5, 2026

Best regards,
Your Company

## Why Approval Required
- New email recipient (first time sending to this address)
- Contains financial document attachment

## Instructions
1. Review the email content above
2. Verify recipient email address
3. Check attachment is correct
4. To approve: Move this file to `/Approved/`
5. To reject: Move this file to `/Rejected/`
6. To modify: Edit this file, then move to Approved

## Expiry
This approval request expires on: 2026-04-07 10:30:00

---
*Created by AI Employee at 2026-04-06 10:30*
```

## How It Works

### 1. AI Detects Sensitive Action
AI Employee determines an action requires approval based on:
- Action type (payment, new email, etc.)
- Recipient status (new vs. known)
- Amount thresholds
- Irreversibility

### 2. Creates Approval Request
AI writes approval file to `Pending_Approval/` with:
- Action details
- Context and reasoning
- Clear instructions
- Expiry timestamp

### 3. Human Reviews
User opens `Pending_Approval/` folder and:
- Reviews pending requests
- Checks details and context
- Decides to approve or reject

### 4. Takes Action
- **Approve**: Move file to `/Approved/`
- **Reject**: Move file to `/Rejected/` with reason

### 5. AI Processes Result
Orchestrator monitors folders:
- **Approved**: Executes the action
- **Rejected**: Logs rejection, notifies AI

## Approval Thresholds

Configure thresholds in your `Company_Handbook.md`:

```markdown
## Approval Thresholds

### Email
- Auto-approve: Known contacts (in contacts.md)
- Require approval: New recipients
- Always block: Bulk sends (>10 recipients)

### Payments
- Auto-approve: Recurring payments < $50
- Require approval: All new payees
- Always block: Payments > $100

### Social Media
- Auto-approve: Scheduled posts (pre-reviewed)
- Require approval: First-time posts
- Always block: Replies to controversial topics

### File Operations
- Auto-approve: Create, read
- Require approval: Move, rename
- Always block: Delete
```

## Orchestrator Integration

The orchestrator monitors approval folders:

```python
# Check for approved files
approved = orchestrator.get_approved()
for approval_file in approved:
    # Execute the approved action
    execute_approved_action(approval_file)
    # Move to Done
    move_to_done(approval_file)
    # Log the action
    log_action(approval_file, 'approved_and_executed')

# Check for rejected files
rejected = orchestrator.get_rejected()
for rejection_file in rejected:
    # Log the rejection
    log_action(rejection_file, 'rejected')
    # Notify AI to take alternative action
    notify_ai_rejection(rejection_file)
```

## Dashboard Integration

Pending approvals shown in Dashboard.md:

```markdown
## Pending Approvals (3)
- [HIGH] Email to client@company.com - Invoice #1234
- [NORMAL] Social post - Service announcement
- [HIGH] Payment to vendor - $250

## Recently Approved (2)
- [✓] Email to partner@business.com - Proposal
- [✓] Social post - Success story

## Recently Rejected (1)
- [✗] Bulk email campaign - Too promotional
```

## Usage Examples

### Example 1: Email Approval

1. **AI Creates Request**:
   ```
   /Pending_Approval/EMAIL_invoice_client_20260406.md
   ```

2. **User Reviews**: Opens file, checks recipient and content

3. **User Approves**: Moves to `/Approved/`

4. **Orchestrator Executes**: Sends email via Email MCP

5. **Completion**: File moved to `/Done/`

### Example 2: Payment Rejection

1. **AI Creates Request**:
   ```
   /Pending_Approval/PAYMENT_vendor_xyz_20260406.md
   ```

2. **User Reviews**: Notices incorrect amount

3. **User Rejects**: Moves to `/Rejected/` with comment:
   ```markdown
   ## Rejection Reason
   Incorrect amount. Should be $1,200 not $1,500.
   Please regenerate invoice with correct amount.
   ```

4. **AI Processes**: Logs rejection, creates corrected request

## Best Practices

1. **Always Review Before Approving**: Check all details carefully
2. **Add Comments**: When rejecting, explain why
3. **Timely Response**: Don't let approvals pile up
4. **Check Expiry**: Expired approvals need regeneration
5. **Audit Regularly**: Review approval logs weekly
6. **Update Thresholds**: Adjust based on trust patterns

## Security Considerations

1. **Never Share Approval Files**: They may contain sensitive info
2. **Verify Recipients**: Double-check email addresses and payment details
3. **Watch for Phishing**: AI may miss sophisticated social engineering
4. **Log Everything**: Maintain complete audit trail
5. **Regular Reviews**: Check approval patterns for anomalies

## Troubleshooting

### Approvals Not Processing
- Check orchestrator is running
- Verify file was moved to correct folder
- Review orchestrator logs for errors

### Too Many Approval Requests
- Review and adjust auto-approve thresholds
- Add known contacts to allowlist
- Check if AI is being overly cautious

### Expired Approvals
- Increase expiry duration in settings
- Review why approvals aren't being processed timely
- Consider extending for low-risk actions

## Next Steps (Gold Tier Enhancements)

- Approval notifications (email, WhatsApp)
- Batch approvals (approve multiple at once)
- Approval delegation (different people for different types)
- Approval analytics (response times, patterns)
- Mobile-friendly approval interface
- Conditional approvals (approve if X, reject if Y)
