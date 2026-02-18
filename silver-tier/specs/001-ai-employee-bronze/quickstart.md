# Quickstart Guide: Personal AI Employee Bronze Tier

**Version**: 1.0.0
**Last Updated**: 2026-02-15

## Overview

The Personal AI Employee Bronze Tier is a Python-based automation system that monitors a folder for new files, captures them as tasks in an Obsidian vault, and uses Claude AI to generate actionable plans. This guide will help you set up and start using the system in under 10 minutes.

## Prerequisites

- **Python**: Version 3.11 or higher
- **Obsidian**: Installed on your system (for viewing the vault)
- **Claude API Key**: From Anthropic (sign up at https://console.anthropic.com)
- **Operating System**: Windows, macOS, or Linux

## Installation

### Step 1: Clone or Download the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd ai-employee-bronze
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -e .
```

This will install:
- anthropic (Claude API client)
- watchdog (file system monitoring)
- python-frontmatter (markdown parsing)
- python-dotenv (configuration)
- tenacity (retry logic)
- pytest (testing framework)

## Configuration

### Step 1: Create Configuration File

Copy the example configuration file:

```bash
cp .env.example .env
```

### Step 2: Add Your Claude API Key

Edit `.env` and add your API key:

```bash
# Required: Your Claude API key from Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Customize paths and behavior
VAULT_PATH=./AI_Employee_Vault
WATCH_FOLDER=./monitored
MAX_ITERATIONS=10
POLL_INTERVAL=60
LOG_LEVEL=INFO
```

**Important**: Never commit `.env` to git. It's already in `.gitignore`.

### Step 3: Initialize the Vault

Create the Obsidian vault structure:

```bash
python -m ai_employee init --vault-path ./AI_Employee_Vault
```

This creates:
- `/Inbox` - For future use
- `/Needs_Action` - Active tasks waiting for plans
- `/Done` - Completed tasks
- `/Plans` - AI-generated action plans
- `Dashboard.md` - System status and activity
- `Company_Handbook.md` - Behavioral rules

### Step 4: Create Monitored Folder

Create a folder for files you want to monitor:

```bash
mkdir monitored
```

## Usage

### Starting the AI Employee

Run the system with default settings:

```bash
python -m ai_employee run
```

Or customize the behavior:

```bash
python -m ai_employee run \
  --vault-path ./AI_Employee_Vault \
  --watch-folder ./monitored \
  --max-iterations 20 \
  --log-level DEBUG
```

### What Happens Next

1. **File Monitoring**: The system watches the `monitored` folder for new files
2. **Task Creation**: New files are converted to markdown tasks in `/Needs_Action`
3. **Plan Generation**: Claude analyzes each task and creates an action plan
4. **Task Completion**: Processed tasks are moved to `/Done`
5. **Dashboard Updates**: `Dashboard.md` shows current status and recent activity

### Viewing Your Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `AI_Employee_Vault`
4. Open `Dashboard.md` to see system status

## Testing the System

### Quick Test: Add a Sample File

1. Create a test file in the monitored folder:

```bash
echo "Review the Q1 sales report and prepare summary for team meeting" > monitored/sales_report.txt
```

2. Wait up to 60 seconds for detection

3. Check the vault:
   - New task appears in `/Needs_Action/task-{uuid}.md`
   - Plan appears in `/Plans/plan-{uuid}.md`
   - Task moves to `/Done/task-{uuid}.md`
   - Dashboard updates with activity

### Expected Output

**Task File** (`/Needs_Action/task-{uuid}.md`):
```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
title: "Review Sales Report"
source_path: "/path/to/monitored/sales_report.txt"
created_at: "2026-02-15T10:30:00Z"
status: "needs_action"
---

# Review Sales Report

Review the Q1 sales report and prepare summary for team meeting
```

**Plan File** (`/Plans/plan-{uuid}.md`):
```markdown
---
id: "660e8400-e29b-41d4-a716-446655440001"
task_id: "550e8400-e29b-41d4-a716-446655440000"
created_at: "2026-02-15T10:31:00Z"
---

# Action Plan: Review Sales Report

## Steps

1. Open the Q1 sales report file
2. Review key metrics (revenue, growth, trends)
3. Identify highlights and concerns
4. Prepare 1-page summary with key points
5. Schedule team meeting to present findings
```

## Customizing the Company Handbook

The `Company_Handbook.md` file controls how the AI generates plans. Edit it to add your own rules:

### Example: Add a New Rule

```markdown
## High Priority Rules

### Require approval for vendor contracts
**Keywords**: contract, vendor, agreement, NDA
**Action**: require_approval

Any task involving vendor contracts must include an approval checkpoint before signing.
```

### Rule Actions

- **flag**: Highlight the task (for urgent items)
- **require_approval**: Insert approval checkpoint in plan
- **warn**: Add warning message to plan
- **block**: Prevent plan generation entirely

Changes take effect immediately (hot reload).

## Common Tasks

### View System Status

Open `Dashboard.md` in Obsidian to see:
- Task counts (Needs Action, Completed, Errors)
- Recent activity (last 10 actions)
- System configuration

### Check Logs

View detailed logs:

```bash
tail -f AI_Employee_Vault/activity.log
```

Log format:
```
[2026-02-15T10:30:00Z] INFO file_detected N/A Detected new file: sales_report.txt success
[2026-02-15T10:30:15Z] INFO task_created 550e8400... Created task: Review Sales Report success
[2026-02-15T10:31:00Z] INFO plan_generated 550e8400... Generated plan with 5 steps success
```

### Stop the System

Press `Ctrl+C` to gracefully stop the AI Employee.

### Restart After Changes

If you modify `.env` or `Company_Handbook.md`:

```bash
# Stop the system (Ctrl+C)
# Restart
python -m ai_employee run
```

## Troubleshooting

### Issue: "API key not found"

**Solution**: Check that `.env` file exists and contains `ANTHROPIC_API_KEY=sk-ant-...`

```bash
# Verify .env exists
cat .env | grep ANTHROPIC_API_KEY
```

### Issue: "Permission denied" when accessing folders

**Solution**: Ensure you have read/write permissions:

```bash
# On macOS/Linux
chmod -R u+rw AI_Employee_Vault monitored

# On Windows
# Right-click folder → Properties → Security → Edit permissions
```

### Issue: Files not being detected

**Solution**: Check the watch folder path:

```bash
# Verify folder exists
ls -la monitored

# Check logs for errors
tail -20 AI_Employee_Vault/activity.log
```

### Issue: Claude API errors

**Solution**: Check API key validity and rate limits:

```bash
# Test API key
python -c "import anthropic; client = anthropic.Anthropic(); print('API key valid')"

# Check rate limits in logs
grep "rate limit" AI_Employee_Vault/activity.log
```

### Issue: Plans not being generated

**Solution**: Check task content and handbook rules:

1. Open the task file in `/Needs_Action`
2. Verify content is readable
3. Check if any handbook rules block plan generation
4. Review logs for Claude API errors

## Advanced Configuration

### Custom Vault Location

```bash
python -m ai_employee run --vault-path /path/to/custom/vault
```

### Multiple Monitored Folders

Bronze tier supports one folder. For multiple sources, upgrade to Silver tier.

### Adjust Processing Speed

```bash
# Process more tasks per cycle
python -m ai_employee run --max-iterations 20

# Faster file detection (not recommended, higher CPU usage)
# Edit .env: POLL_INTERVAL=30
```

### Debug Mode

```bash
python -m ai_employee run --log-level DEBUG
```

This shows detailed information about:
- File system events
- API requests and responses
- Handbook rule matching
- Error stack traces

## Best Practices

### 1. Start Small

Begin with a few test files to understand the workflow before processing real work items.

### 2. Review Plans Before Executing

The AI generates plans, but you execute them. Always review plans for accuracy and appropriateness.

### 3. Customize the Handbook

Add rules specific to your workflow and preferences. The default rules are just a starting point.

### 4. Monitor the Dashboard

Check `Dashboard.md` regularly to ensure the system is operating correctly.

### 5. Back Up Your Vault

Use Obsidian Sync or manual backups to protect your task history.

### 6. Keep API Key Secure

Never share your `.env` file or commit it to version control.

## Next Steps

### After Setup

1. **Add real tasks**: Place actual work files in the monitored folder
2. **Refine handbook**: Add rules specific to your workflow
3. **Review plans**: Check AI-generated plans for quality
4. **Provide feedback**: Note what works well and what needs improvement

### Upgrading to Silver Tier

When you're ready for more features:
- Gmail integration
- Multiple input sources
- Task prioritization
- Advanced scheduling

Contact support or check documentation for upgrade path.

## Getting Help

### Documentation

- Full specification: `specs/001-ai-employee-bronze/spec.md`
- Architecture plan: `specs/001-ai-employee-bronze/plan.md`
- Data model: `specs/001-ai-employee-bronze/data-model.md`

### Support

- GitHub Issues: Report bugs and request features
- Community Forum: Ask questions and share tips
- Email Support: support@example.com

## Appendix: CLI Reference

### Commands

```bash
# Initialize vault
python -m ai_employee init [--vault-path PATH]

# Run the AI Employee
python -m ai_employee run [OPTIONS]

# Check configuration
python -m ai_employee config [--show]

# Validate handbook
python -m ai_employee validate-handbook [--handbook PATH]

# Show version
python -m ai_employee --version
```

### Options for `run` Command

| Option | Description | Default |
|--------|-------------|---------|
| `--vault-path` | Path to Obsidian vault | `./AI_Employee_Vault` |
| `--watch-folder` | Folder to monitor | `./monitored` |
| `--max-iterations` | Max tasks per cycle | `10` |
| `--log-level` | Logging verbosity | `INFO` |
| `--no-dashboard` | Skip dashboard updates | `False` |
| `--dry-run` | Test without creating files | `False` |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `VAULT_PATH` | Default vault path | No |
| `WATCH_FOLDER` | Default monitored folder | No |
| `MAX_ITERATIONS` | Default max iterations | No |
| `LOG_LEVEL` | Default log level | No |

## License

[Your license information here]

## Version History

- **1.0.0** (2026-02-15): Initial Bronze tier release
