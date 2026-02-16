# Personal AI Employee - Bronze Tier

A foundational AI Employee that monitors a folder for new files, captures them as tasks in an Obsidian vault, and generates actionable plans using Claude AI.

## Features

- **Automated File Monitoring**: Watches vault Inbox folder for new files
- **Task Capture**: Converts files to structured markdown tasks with YAML metadata
- **AI-Powered Planning**: Uses Claude to generate actionable plans based on handbook rules
- **Handbook-Guided Behavior**: Customizable rules for AI decision-making
- **Dashboard Tracking**: Real-time task counts and activity logging
- **Safe Operation**: Never deletes original files, includes approval checkpoints

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Obsidian (optional, for viewing vault)

### Installation

```bash
# Navigate to project directory
cd bronze-tier

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install package
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Initialize Vault

```bash
python -m ai_employee init
```

This creates the vault structure:
```
ai_employee_vault/
├── Inbox/              # Drop files here (monitored)
├── Needs_Action/       # Tasks being processed
├── Done/               # Completed tasks with AI plans
├── Dashboard.md        # Status overview
├── Company_Handbook.md # Behavior rules
└── activity.log        # System log
```

### Run the System

```bash
python -m ai_employee run
```

Expected output:
```
Starting AI Employee...
Vault: ai_employee_vault
Watching: ai_employee_vault\Inbox
[OK] File watcher started
[OK] Monitoring: ai_employee_vault\Inbox
[OK] Processing tasks automatically
```

### Test It

In a **new terminal** (keep the system running):

```bash
# Create a test task
echo "Review Q1 sales report and prepare summary" > ai_employee_vault/Inbox/test.txt

# Wait 10-15 seconds for processing
```

### Verify Results

```bash
# View completed task with AI plan
cat ai_employee_vault/Done/task-*.md

# Check dashboard
cat ai_employee_vault/Dashboard.md

# View activity log
tail -f ai_employee_vault/activity.log
```

## How It Works

1. **File Detection**: System monitors `Inbox/` folder for new files
2. **Task Creation**: Converts files to markdown with YAML metadata in `Needs_Action/`
3. **AI Planning**: Claude reads `Company_Handbook.md` and generates action plan
4. **Plan Integration**: AI plan is appended to the task file
5. **Completion**: Task moved to `Done/` folder
6. **Dashboard Update**: Counts and activity log updated
7. **Preservation**: Original file remains in Inbox (never deleted)

## Customizing Behavior

Edit `ai_employee_vault/Company_Handbook.md` to customize AI behavior:

```markdown
# Company Handbook

## Rules
- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.
- [MEDIUM] Summaries under 200 words.
- [LOW] Use bullet points when possible.
```

Add your own rules to guide the AI's decision-making process.

## CLI Commands

### Initialize Vault
```bash
python -m ai_employee init [--vault-path PATH]
```

### Run System
```bash
python -m ai_employee run [OPTIONS]

Options:
  --vault-path PATH       Path to vault (default: ./ai_employee_vault)
  --watch-folder PATH     Folder to monitor (default: vault/Inbox)
  --max-iterations N      Max tasks per cycle (default: 10)
  --log-level LEVEL       Logging level (default: INFO)
```

### Show Configuration
```bash
python -m ai_employee config --show
```

## Project Structure

```
bronze-tier/
├── ai_employee/           # Source code
│   ├── models/           # Data models (Task, Plan, LogEntry)
│   ├── vault/            # Vault management and dashboard
│   ├── watcher/          # File monitoring and task creation
│   ├── processor/        # Task processing and Claude integration
│   └── utils/            # Logging and utilities
├── tests/                # Test suite
├── specs/                # Design documents
├── README.md             # This file
├── QUICKSTART.md         # 5-minute setup guide
├── TESTING.md            # Comprehensive testing procedures
├── CHANGES.md            # Technical change log
└── requirements.txt      # Python dependencies
```

## Architecture

- **Language**: Python 3.11+
- **File Monitoring**: watchdog library
- **AI Integration**: Anthropic SDK (Claude 3.5 Sonnet)
- **Storage**: File-based (markdown with YAML frontmatter)
- **Vault Format**: Obsidian-compatible markdown

## Success Criteria

- ✓ Detects files within 60 seconds
- ✓ Generates plans in under 10 seconds per task
- ✓ Processes 10 tasks in under 5 minutes
- ✓ Zero autonomous sensitive actions without approval
- ✓ 24-hour uptime without crashes
- ✓ Never deletes original files

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Verify `.env` file exists in `bronze-tier/` directory
- Check it contains: `ANTHROPIC_API_KEY=sk-ant-...`
- No quotes needed around the key

### "No module named 'ai_employee'"
- Run: `pip install -e .` from `bronze-tier/` directory
- Activate virtual environment if using one

### Files not being detected
- Verify files are in `ai_employee_vault/Inbox/`
- Check console output for errors
- View logs: `tail -f ai_employee_vault/activity.log`

### Plans not generated
- Verify API key is valid and active
- Check internet connection
- Look for rate limit errors in logs
- Ensure Claude API is accessible

### Permission errors
- Check read/write permissions on vault directory
- Run with appropriate user permissions

## Testing

Run the integration test suite:

```bash
# Run all tests
pytest

# Run specific test
python tests/test_bronze_tier.py

# Run with verbose output
pytest -v
```

See `TESTING.md` for comprehensive testing procedures.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black ai_employee tests

# Lint code
pylint ai_employee
flake8 ai_employee

# Type checking
mypy ai_employee
```

## Documentation

- **README.md** (this file) - Main documentation and quick start
- **QUICKSTART.md** - 5-minute setup guide with examples
- **TESTING.md** - Comprehensive testing procedures
- **CHANGES.md** - Technical change log and implementation details
- **specs/** - Detailed specifications and architecture documents

## Limitations (Bronze Tier)

By design, Bronze Tier has these limitations:
- Single source monitoring (Inbox folder only)
- No Gmail integration (planned for Silver/Gold tiers)
- No task prioritization (FIFO processing)
- No web interface (Obsidian only)
- Manual plan execution (no autonomous actions)
- Local storage only (no cloud sync)

## Roadmap

- **Silver Tier**: Gmail integration, task prioritization
- **Gold Tier**: Multi-source monitoring, web interface, autonomous execution

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Version

1.0.0 - Bronze Tier Release

## Support

For issues, questions, or contributions:
- Check `TESTING.md` for troubleshooting
- Review `CHANGES.md` for technical details
- See `specs/` for architecture documentation

---

**Status**: Production Ready ✓
