# Plan Generator Skill

Automatically create structured Plan.md files for tasks requiring multi-step execution.

## Overview

This skill enables your AI Employee to analyze action files and create detailed, step-by-step plans before execution. Plans include objectives, action items, dependencies, approval requirements, and success criteria.

## Features

- **Action Analysis**: Reads action files and determines required steps
- **Dependency Tracking**: Identifies prerequisites and blocking factors
- **Approval Detection**: Flags actions requiring human-in-the-loop approval
- **Status Tracking**: Plans track progress through execution stages
- **Template-Based**: Uses structured templates for consistency
- **Priority Assessment**: Determines urgency based on action metadata

## How It Works

1. **Trigger**: Orchestrator detects new action file in `Needs_Action/`
2. **Analysis**: AI reads action content and metadata
3. **Plan Creation**: Generates structured Plan.md in `Plans/` folder
4. **Execution**: AI follows plan steps, checking off items
5. **Completion**: Moves action to `Done/` when all steps complete

## Plan File Format

```markdown
---
created: 2026-04-06T10:30:00Z
status: pending_approval
action_file: EMAIL_abc123_20260406.md
action_type: email
priority: high
estimated_steps: 5
completed_steps: 0
---

# Plan: Process Client Invoice Request

## Objective
Respond to client's invoice request by generating and sending the January invoice.

## Context
- **Source**: EMAIL_abc123_20260406.md
- **From**: client@company.com
- **Subject**: Invoice Request - January Services
- **Priority**: High
- **Received**: 2026-04-06 10:30:00

## Steps
- [x] 1. Identify client and service details
  - Client: Company ABC
  - Service: Monthly consulting retainer
  - Amount: $1,500
  
- [x] 2. Generate invoice PDF
  - Use invoice template
  - Fill in client details and amount
  - Save to /Vault/Invoices/2026-04_Company_ABC.pdf
  
- [ ] 3. Create email response
  - Draft professional email
  - Attach invoice PDF
  - Review before sending
  
- [ ] 4. Send email (REQUIRES APPROVAL)
  - To: client@company.com
  - Subject: January 2026 Invoice - $1,500
  - Attachment: Invoice PDF
  - **Status**: Pending human approval
  
- [x] 5. Log transaction
  - Update /Accounting/Current_Month.md
  - Record invoice sent and amount

## Dependencies
- None identified

## Approval Required
✅ Step 4 requires human approval before sending email.
See `/Pending_Approval/EMAIL_invoice_company_abc.md`

## Success Criteria
- [ ] Invoice generated with correct details
- [ ] Email sent to client with attachment
- [ ] Transaction logged in accounting system
- [ ] Action file moved to /Done/

## Notes
- Client has been invoiced before - use same template
- Payment terms: Net 30
- Follow up if not paid within 15 days

---
*Created by AI Employee at 2026-04-06 10:30*
```

## Plan Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Plan created, not yet started |
| `in_progress` | Steps being executed |
| `pending_approval` | Waiting for human approval |
| `completed` | All steps finished |
| `blocked` | Cannot proceed (missing info, error) |
| `cancelled` | Plan abandoned |

## Integration with Orchestrator

The Plan Generator works with the main orchestration flow:

1. **Action Detected**: Watcher creates file in `Needs_Action/`
2. **Plan Created**: AI generates plan and saves to `Plans/`
3. **Approval Workflow**: If needed, creates approval request
4. **Step Execution**: AI executes steps, updating checkboxes
5. **Completion**: Action moved to `Done/`, plan marked complete

## Example Workflow

### Scenario: Client Asks for Invoice

**Step 1**: Gmail Watcher creates action file
```
/Needs_Action/EMAIL_xyz789_20260406.md
```

**Step 2**: Plan Generator creates plan
```
/Plans/PLAN_process_invoice_request_20260406.md
```

**Step 3**: AI executes initial steps
- ✅ Identifies client details
- ✅ Generates invoice

**Step 4**: Approval needed for sending
```
/Pending_Approval/EMAIL_invoice_client.md
```

**Step 5**: Human approves

**Step 6**: AI completes remaining steps
- ✅ Sends email
- ✅ Logs transaction
- ✅ Moves to Done

## Usage

Plans are created automatically by the AI Employee when processing action files. No manual invocation needed.

### Manual Plan Creation

If you want to create a plan manually:

```bash
# Ask AI to create a plan
qwen "Create a plan for processing the invoice request in Needs_Action/EMAIL_xyz.md"
```

## Best Practices

1. **Be Specific**: Each step should be clear and actionable
2. **Identify Dependencies**: Note what must happen before each step
3. **Flag Approvals**: Clearly mark steps requiring human approval
4. **Track Progress**: Update checkboxes as steps complete
5. **Define Success**: Include clear completion criteria
6. **Add Context**: Include relevant metadata from the original action

## Next Steps (Gold Tier Enhancements)

- Auto-generate sub-plans for complex steps
- Cross-plan dependency tracking
- Time estimation for each step
- Plan templates for common actions
- Historical plan performance tracking
