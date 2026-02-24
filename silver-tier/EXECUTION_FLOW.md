# AI Employee Silver Tier - Execution Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OS-LEVEL SCHEDULER                        │
│              (Windows Task Scheduler)                        │
│                                                              │
│  Runs every 15 minutes:                                     │
│  python -m ai_employee.runner                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI EMPLOYEE RUNNER                         │
│                  (ai_employee/runner.py)                     │
│                                                              │
│  Fully automated workflow - NO manual intervention          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐              ┌──────────────┐
│ FILE WATCHER │              │GMAIL WATCHER │
│              │              │              │
│ Scans Inbox/ │              │ IMAP polling │
│ for new files│              │ for emails   │
└──────┬───────┘              └──────┬───────┘
       │                             │
       └──────────┬──────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  NEEDS_ACTION/ │
         │  (Task files)  │
         └────────┬───────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING SKILL                           │
│              (ai_employee/skills/reasoning_skill.py)         │
│                                                              │
│  • Analyzes task content                                    │
│  • Detects action type (email, linkedin, research, etc.)    │
│  • Extracts entities (emails, URLs, amounts, dates)         │
│  • Reads Company Handbook rules                             │
│  • Generates action steps                                   │
│  • Identifies approval checkpoints                          │
│  • Creates Plan.md file                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │    Plans/      │
              │  plan-{id}.md  │
              └────────┬───────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
  ┌─────────────┐            ┌─────────────┐
  │ NO APPROVAL │            │  APPROVAL   │
  │   NEEDED    │            │  REQUIRED   │
  └──────┬──────┘            └──────┬──────┘
         │                          │
         ▼                          ▼
  ┌─────────────┐         ┌──────────────────┐
  │    Done/    │         │ APPROVAL SKILL   │
  │             │         │                  │
  │ (Research,  │         │ Creates approval │
  │  queries)   │         │ request file     │
  └─────────────┘         └────────┬─────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │Waiting_Approval/│
                          │                 │
                          │ approval-{id}.md│
                          └────────┬────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                          │  HUMAN REVIEW   │
                          │                 │
                          │ Creates:        │
                          │ APPROVED.txt or │
                          │ REJECTED.txt    │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
            ┌──────────────┐            ┌──────────────┐
            │   APPROVED   │            │   REJECTED   │
            └──────┬───────┘            └──────┬───────┘
                   │                           │
                   ▼                           ▼
         ┌──────────────────┐          ┌─────────────┐
         │ EXECUTION QUEUE  │          │  Rejected/  │
         │                  │          │             │
         │ LinkedIn_Posts/  │          │ (Archived)  │
         │ post-{id}.md     │          └─────────────┘
         └────────┬─────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              LINKEDIN EXECUTION SKILL                        │
│        (ai_employee/skills/linkedin_execution_skill.py)      │
│                                                              │
│  • Reads post content from LinkedIn_Posts/                  │
│  • Calls linkedin_post_skill.publish()                      │
│  • Posts via REAL LinkedIn API (OAuth 2.0)                  │
│  • Returns actual post ID from LinkedIn                     │
│  • Moves completed files to Done/                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  LINKEDIN API  │
              │                │
              │ POST /ugcPosts │
              │                │
              │ Returns post ID│
              └────────┬───────┘
                       │
                       ▼
                ┌─────────────┐
                │    Done/    │
                │             │
                │ post-{id}.md│
                │ plan-{id}.md│
                │ task-{id}.md│
                └─────────────┘
```

## Component Details

### 1. OS-Level Scheduler (Windows Task Scheduler)

**Type:** OS-level (NOT application-level)
**Frequency:** Every 15 minutes
**Command:** `python -m ai_employee.runner`
**Survives:** System reboots
**Runs:** Whether user is logged in or not

**Setup:**
```powershell
.\scripts\setup_windows_scheduler.ps1
```

### 2. AI Employee Runner

**File:** `ai_employee/runner.py`
**Type:** Fully automated Python workflow
**No:** Manual intervention, subprocess calls, CLI AI execution

**Steps:**
1. Capture inputs (files + emails)
2. Generate plans (reasoning skill)
3. Process approvals (approval skill)
4. Execute actions (LinkedIn, email)

### 3. Watchers (2 Required)

#### File Watcher
- **Path:** `ai_employee/watchers/file_watcher.py`
- **Monitors:** `ai_employee_vault/Inbox/`
- **Creates:** Task files in `Needs_Action/`
- **Tracks:** Processed files to avoid duplicates

#### Gmail Watcher
- **Path:** `ai_employee/watchers/gmail_watcher.py`
- **Protocol:** IMAP (no OAuth complexity)
- **Monitors:** Unread emails
- **Creates:** Task files in `Needs_Action/`
- **Marks:** Emails as read after processing

### 4. Reasoning Skill (Claude Reasoning Loop)

**File:** `ai_employee/skills/reasoning_skill.py`
**Type:** Agent Skill (NO subprocess, NO CLI)

**Process:**
1. Reads task content
2. Detects action type (pattern matching)
3. Extracts entities (regex)
4. Reads Company Handbook
5. Generates action steps
6. Identifies approval checkpoints
7. Creates warnings
8. Saves Plan.md

**Output:** `Plans/plan-{task_id}.md`

### 5. Approval Skill (Human-in-the-Loop)

**File:** `ai_employee/skills/approval_skill.py`
**Type:** Agent Skill

**Process:**
1. Creates approval request file
2. Waits for human decision
3. Checks for APPROVED.txt or REJECTED.txt
4. Moves to appropriate folder
5. Handles timeouts (24 hours default)

**Human Action:**
- Create `APPROVED.txt` in `Waiting_Approval/` to approve
- Create `REJECTED.txt` in `Waiting_Approval/` to reject

### 6. LinkedIn Execution Skill

**File:** `ai_employee/skills/linkedin_execution_skill.py`
**Type:** Agent Skill

**Process:**
1. Reads post content from `LinkedIn_Posts/`
2. Calls `linkedin_post_skill.publish()`
3. Posts via REAL LinkedIn API
4. Returns actual post ID
5. Moves to `Done/`

### 7. LinkedIn Post Skill (Real API)

**File:** `ai_employee/skills/linkedin_post_skill.py`
**Type:** Agent Skill with OAuth 2.0

**Features:**
- OAuth 2.0 authorization code flow
- Automatic token refresh
- Secure token storage
- Rate limit handling
- Real LinkedIn API v2 integration

**Setup:**
```bash
python -m ai_employee.skills.linkedin_post_skill
```

### 8. MCP Server

**File:** `ai_employee/mcp/mcp_server.py`
**Type:** External action orchestrator

**Tools:**
- `send_email`: Gmail API or SMTP fallback
- `post_linkedin`: Real LinkedIn API (via linkedin_post_skill)

**NO MORE:** Simulated posting, markdown file creation

## Data Flow

### Task Lifecycle

```
1. INPUT
   File dropped in Inbox/ OR Email received
   ↓
2. CAPTURE
   Watcher creates task-{id}.md in Needs_Action/
   ↓
3. REASONING
   Reasoning skill generates plan-{id}.md in Plans/
   ↓
4. ROUTING
   If approval needed → Waiting_Approval/
   If no approval → Done/
   ↓
5. APPROVAL (if needed)
   Human creates APPROVED.txt or REJECTED.txt
   ↓
6. EXECUTION (if approved)
   LinkedIn: Post via API → Done/
   Email: Send via MCP → Done/
   ↓
7. COMPLETION
   All files moved to Done/
   Logged in activity.log
```

### File Structure

```
ai_employee_vault/
├── Inbox/                    # Input: New files
├── Needs_Action/             # Tasks awaiting processing
│   └── task-{id}.md
├── Plans/                    # Generated plans
│   └── plan-{id}.md
├── Waiting_Approval/         # Tasks awaiting approval
│   ├── approval-{id}.md
│   ├── APPROVED.txt          # Human creates this
│   └── REJECTED.txt          # Or this
├── Approved/                 # Approved requests (archived)
│   └── approval-{id}.md
├── Rejected/                 # Rejected requests (archived)
│   └── approval-{id}.md
├── LinkedIn_Posts/           # Approved posts ready to execute
│   └── post-{id}.md
├── Done/                     # Completed tasks
│   ├── task-{id}.md
│   ├── plan-{id}.md
│   └── post-{id}.md
└── activity.log              # All actions logged
```

## Key Differences from Previous Implementation

### ❌ OLD (Fake/Manual)

- **Scheduler:** Python `schedule` library (application-level)
- **LinkedIn:** Markdown file creation (simulated)
- **Runner:** Prints instructions for Claude Code to process manually
- **Reasoning:** Not integrated into automated flow
- **Approval:** Not connected to execution
- **Execution:** Manual copy-paste to LinkedIn

### ✅ NEW (Production)

- **Scheduler:** Windows Task Scheduler (OS-level)
- **LinkedIn:** Real API via OAuth 2.0
- **Runner:** Fully automated Python workflow
- **Reasoning:** Automatically generates plans
- **Approval:** Automatically gates execution
- **Execution:** Real API calls with actual post IDs

## Verification

### Check Scheduler
```powershell
Get-ScheduledTask -TaskName "AI-Employee-Silver"
```

### Check Last Run
```powershell
Get-ScheduledTask -TaskName "AI-Employee-Silver" | Get-ScheduledTaskInfo
```

### View Logs
```powershell
Get-Content logs\scheduler.log -Tail 50
```

### Manual Test
```bash
python -m ai_employee.runner
```

### Test LinkedIn Auth
```bash
python -m ai_employee.skills.linkedin_post_skill
```

## Troubleshooting

### Scheduler Not Running
1. Check task exists: `Get-ScheduledTask -TaskName "AI-Employee-Silver"`
2. Check task is enabled (State = Ready)
3. Run manually: `Start-ScheduledTask -TaskName "AI-Employee-Silver"`
4. Check logs: `logs/scheduler.log`

### LinkedIn Not Posting
1. Check OAuth: `python -m ai_employee.skills.linkedin_post_skill`
2. Check credentials in `.env`: `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`
3. Check token file: `ai_employee_vault/.linkedin_tokens.json`
4. Re-authenticate if needed

### Plans Not Generated
1. Check tasks exist: `ls ai_employee_vault/Needs_Action/`
2. Run manually: `python -m ai_employee.runner`
3. Check logs for errors
4. Verify reasoning_skill is working

### Approvals Not Processing
1. Check approval files exist: `ls ai_employee_vault/Waiting_Approval/`
2. Create `APPROVED.txt` or `REJECTED.txt` in that folder
3. Wait for next scheduler run (or run manually)
4. Check logs for processing results
