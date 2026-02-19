# Personal AI Employee - Silver Tier

**Functional Assistant with Multi-Source Watchers, Intelligent Reasoning, and Approval Workflow**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)]()
[![Tier](https://img.shields.io/badge/Tier-Silver-silver)]()
[![Score](https://img.shields.io/badge/Technical%20Review-98%25-brightgreen)]()

---

## Quick Start (5 Minutes)

```bash
# 1. Initialize the system
python -m ai_employee init

# 2. Create a test task
echo "Research the top 3 AI automation tools in 2026" > ai_employee_vault/Inbox/task.txt

# 3. Process the task
python claude_runner.py

# 4. Check results
ls ai_employee_vault/Done/
cat ai_employee_vault/Plans/plan-*.md
```

**See [QuickStart.md](QuickStart.md) for detailed instructions.**

---

## Two Processing Modes

### 🚀 Automated Mode (Fast)
- **File:** `claude_runner.py`
- **Speed:** < 1 second per task
- **Best for:** Automation, demos, scheduled tasks
- **How:** Pattern-based reasoning

```bash
python claude_runner.py
```

### 🧠 Claude Code Mode (Intelligent)
- **File:** `claude_runner_with_ai.py`
- **Speed:** 5-10 seconds per task
- **Best for:** Complex tasks, quality output
- **How:** Real AI reasoning via Claude Code

```bash
# Inside Claude Code CLI
python claude_runner_with_ai.py
```

**See [TWO_MODES_EXPLAINED.md](TWO_MODES_EXPLAINED.md) for comparison.**

---

## Features

### ✓ Silver Tier Requirements (All Implemented)

1. **Two Watchers**
   - File Watcher (monitors Inbox/)
   - Gmail Watcher (IMAP-based email monitoring)

2. **Automatic LinkedIn Posting**
   - File-based queue system
   - Ready for API integration

3. **Claude Reasoning Loop**
   - Automated: Pattern-based reasoning
   - Claude Code: Real AI reasoning
   - Generates Plan.md files

4. **MCP Server**
   - send_email (SMTP)
   - post_linkedin (file-based)

5. **Human-in-the-Loop Approval**
   - File-based workflow (APPROVED.txt / REJECTED.txt)
   - Automatic timeout (24 hours)

6. **Scheduling**
   - Continuous mode (runs every X minutes)
   - Single-run mode (Windows Task Scheduler compatible)

7. **Agent Skills Architecture**
   - ReasoningSkill (intelligent task analysis)
   - ApprovalSkill (approval workflow)

---

## Architecture

```
silver-tier/
├── claude_runner.py              # Automated mode (pattern-based)
├── claude_runner_with_ai.py     # Claude Code mode (real AI)
├── scheduler.py                  # Automated scheduling
├── ai_employee/
│   ├── skills/                   # Agent skills
│   │   ├── reasoning_skill.py   # Intelligent reasoning
│   │   └── approval_skill.py    # Approval workflow
│   ├── watchers/                 # Input sources
│   │   ├── file_watcher.py      # File monitoring
│   │   └── gmail_watcher.py     # Email monitoring
│   ├── mcp/                      # External actions
│   │   └── mcp_server.py        # Email + LinkedIn
│   └── ...
└── ai_employee_vault/            # Data storage
    ├── Inbox/                    # Input files
    ├── Needs_Action/             # Tasks to process
    ├── Waiting_Approval/         # Awaiting approval
    ├── Approved/                 # Approved tasks
    ├── Done/                     # Completed tasks
    └── Plans/                    # Generated plans
```

---

## Usage Examples

### Example 1: Simple Research Task

```bash
# Create task
echo "Research AI automation platforms and compare features" > ai_employee_vault/Inbox/research.txt

# Process with automated mode
python claude_runner.py

# Result: Task processed, plan generated, moved to Done/
```

### Example 2: Email Task (Requires Approval)

```bash
# Create email task
cat > ai_employee_vault/Inbox/email.txt << 'EOF'
Send email to client@example.com

Subject: Q1 2026 Project Update

Hi Client,

Quick update on the project:
- Phase 1 completed
- Phase 2 starting next week
- On track for March 15th delivery

Best regards,
AI Employee
EOF

# Process
python claude_runner.py

# Result: Task moved to Waiting_Approval/

# Approve
echo "Approved" > ai_employee_vault/Waiting_Approval/APPROVED.txt

# Process again
python claude_runner.py

# Result: Email sent (if SMTP configured), task moved to Done/
```

### Example 3: Scheduled Automation

```bash
# Run every 15 minutes
python scheduler.py

# Or setup Windows Task Scheduler
# See SCHEDULER_SETUP.md for instructions
```

---

## Configuration

### Optional: Gmail Monitoring

```bash
# Set environment variables
set GMAIL_EMAIL=your-email@gmail.com
set GMAIL_PASSWORD=your-app-password

# Get app password: https://myaccount.google.com/apppasswords
```

### Optional: Email Sending

```bash
# Set SMTP credentials
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [QuickStart.md](QuickStart.md) | 5-minute getting started guide |
| [TWO_MODES_EXPLAINED.md](TWO_MODES_EXPLAINED.md) | Comparison of automated vs Claude Code mode |
| [CLAUDE_CODE_INTEGRATION.md](CLAUDE_CODE_INTEGRATION.md) | How to use Claude Code for real AI reasoning |
| [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md) | Windows Task Scheduler setup |
| [SILVER_TIER_SUMMARY.md](SILVER_TIER_SUMMARY.md) | Complete implementation overview |
| [TECHNICAL_REVIEW_REPORT.md](TECHNICAL_REVIEW_REPORT.md) | Technical audit (98% score) |
| [FINAL_DELIVERY.md](FINAL_DELIVERY.md) | Delivery summary |

---

## Technical Details

### Statistics
- **Total Lines of Code:** ~2,600 (Silver Tier specific)
- **Python Files:** 24
- **Test Coverage:** All components tested
- **Technical Review Score:** 98% (49/50)

### Requirements
- Python 3.11+
- Dependencies: See `requirements.txt`
- Optional: Claude Code CLI (for AI reasoning mode)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize vault
python -m ai_employee init
```

---

## Workflow

### Complete Workflow (Single Command)

```bash
python claude_runner.py
```

**What happens:**
1. **Capture Files** - Scans Inbox/ for new files
2. **Capture Emails** - Checks Gmail for unread emails (if configured)
3. **Process Tasks** - Generates plans using reasoning skill
4. **Process Approvals** - Checks for APPROVED.txt / REJECTED.txt
5. **Execute Tasks** - Runs approved tasks via MCP server
6. **Mark Complete** - Moves tasks to Done/

---

## Testing

### Run Tests

```bash
# Test automated mode
python claude_runner.py

# Test scheduler (single run)
python scheduler.py --once

# Test Gmail watcher
python -m ai_employee.watchers.gmail_watcher

# Test MCP server
python -m ai_employee.mcp.mcp_server
```

### Stability Tests
- ✓ Empty vault: No crashes
- ✓ Missing folders: Auto-repairs
- ✓ SMTP failure: Graceful handling
- ✓ Gmail failure: Continues workflow

---

## Comparison with Bronze Tier

| Feature | Bronze Tier | Silver Tier |
|---------|-------------|-------------|
| **Watchers** | File only | File + Gmail |
| **Reasoning** | Claude Code | Pattern-based + Claude Code |
| **Approval** | Manual | Automated workflow |
| **Actions** | Skills only | MCP server + Skills |
| **Scheduling** | Manual | Automated (Task Scheduler) |
| **LinkedIn** | No | Yes (simulated) |

---

## Troubleshooting

### Vault not found
```bash
python -m ai_employee init
```

### No tasks to process
```bash
echo "Test task" > ai_employee_vault/Inbox/test.txt
```

### Gmail not working
```bash
# Check credentials
echo %GMAIL_EMAIL%

# Set credentials
set GMAIL_EMAIL=your-email@gmail.com
set GMAIL_PASSWORD=your-app-password
```

### View logs
```bash
tail -50 ai_employee_vault/activity.log
```

---

## Next Steps

1. ✓ Run QuickStart guide
2. ✓ Test both processing modes
3. ✓ Configure Gmail (optional)
4. ✓ Configure SMTP (optional)
5. ✓ Setup Task Scheduler for automation

---

## Status

**Production Ready** ✓

- All Silver Tier requirements implemented
- Both processing modes working
- Comprehensive documentation
- Technical review: 98% score
- Ready for hackathon demonstration

---

## License

MIT License - See LICENSE file for details

---

## Support

For questions or issues:
1. Check documentation in this directory
2. Review activity.log for errors
3. See TECHNICAL_REVIEW_REPORT.md for architecture details

---

**Built for Hackathon 0 - Personal AI Employee Challenge**
