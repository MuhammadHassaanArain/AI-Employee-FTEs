# Approval Request

**Task ID**: 9955f330-df7b-4e91-bcb5-be38c154adfd
**Task Title**: Send email to client about payment
**Created**: 2026-02-19T14:21:47.821942
**Timeout**: 24 hours

## Task Content

Send an email to client@example.com requesting payment of $5000 for invoice #12345. Due date is March 1st.

## Generated Plan

1. Review email content and recipients
2. Verify recipient addresses: client@example.com
3. Draft email message
4. **[APPROVAL REQUIRED]** Request approval before sending
5. **[APPROVAL REQUIRED]** Send email via MCP server
6. Log email sent in activity log


## Handbook Rules Applied



## Warnings

- External communication - review for company policy compliance
- Task originated from email - verify sender authenticity


---

## How to Approve/Reject

To **APPROVE** this action:
1. Create a file named `APPROVED.txt` in the Waiting_Approval folder
2. The system will execute the action

To **REJECT** this action:
1. Create a file named `REJECTED.txt` in the Waiting_Approval folder
2. The system will cancel the action

**Note**: This request will timeout after 24 hours and be automatically rejected.
