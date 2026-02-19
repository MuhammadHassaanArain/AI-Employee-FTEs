# Approval Request

**Task ID**: 1bf52db7-baf2-440c-aaf6-4e05978ad94d
**Task Title**: Send email to client@example.com
**Created**: 2026-02-19T15:01:45.601021
**Timeout**: 24 hours

## Task Content

Send email to client@example.com

  Subject: Project Update

  Please send an email with the following:
  - Project is on track
  - Delivery date: March 15th
  - Next meeting: March 1st

  Best regards,
  AI Employee
  EOF

## Generated Plan

1. Review email content and recipients
2. Verify recipient addresses: client@example.com
3. Draft email message
4. **[APPROVAL REQUIRED]** Request approval before sending
5. **[APPROVAL REQUIRED]** Send email via MCP server
6. Log email sent in activity log


## Handbook Rules Applied

- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.


## Warnings

- External communication - review for company policy compliance


---

## How to Approve/Reject

To **APPROVE** this action:
1. Create a file named `APPROVED.txt` in the Waiting_Approval folder
2. The system will execute the action

To **REJECT** this action:
1. Create a file named `REJECTED.txt` in the Waiting_Approval folder
2. The system will cancel the action

**Note**: This request will timeout after 24 hours and be automatically rejected.
