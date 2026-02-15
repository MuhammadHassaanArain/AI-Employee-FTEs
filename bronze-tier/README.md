# Personal AI Employee - Bronze Tier

A foundational AI Employee that monitors a folder for new files, captures them as tasks in an Obsidian vault, and generates actionable plans using Claude AI.

## Features

- **File Monitoring**: Automatically detects new files in a monitored folder
- **Task Capture**: Converts files to structured tasks in Obsidian vault
- **AI Planning**: Uses Claude to generate actionable plans with approval checkpoints
- **Handbook Rules**: Enforces custom behavioral rules for plan generation
- **Autonomous Operation**: Processes tasks continuously with configurable limits
- **Dashboard**: Real-time status and activity tracking in Obsidian

## Prerequisites

- Python 3.11 or higher
- Obsidian (for viewing the vault)
- Claude API key from Anthropic

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd bronze-tier

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Claude API key
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Initialize Vault

```bash
# Create the Obsidian vault structure
python -m ai_employee init --vault-path ./AI_Employee_Vault
```

### 4. Run the AI Employee

```bash
# Create a folder to monitor
mkdir monitored

# Start the AI Employee
python -m ai_employee run --watch-folder ./monitored
```

### 5. Test It

```bash
# In another terminal, add a test file
echo "Review the Q1 sales report" > monitored/sales_task.txt

# Check the vault in Obsidian:
# - New task appears in /Needs_Action
# - Plan generated in /Plans
# - Task moved to /Done
# - Dashboard updated
```

## Usage

### Commands

```bash
# Initialize vault
python -m ai_employee init [--vault-path PATH]

# Run the AI Employee
python -m ai_employee run [OPTIONS]

# Options for run command:
#   --vault-path PATH       Path to Obsidian vault (default: ./AI_Employee_Vault)
#   --watch-folder PATH     Folder to monitor (default: ./monitored)
#   --max-iterations N      Max tasks per cycle (default: 10)
#   --log-level LEVEL       Logging level (default: INFO)
```

### Customizing Behavior

Edit `AI_Employee_Vault/Company_Handbook.md` to add your own rules:

```markdown
## High Priority Rules

### Require approval for vendor contracts
**Keywords**: contract, vendor, agreement, NDA
**Action**: require_approval

Any task involving vendor contracts must include an approval checkpoint.
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
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── specs/               # Design documents
└── AI_Employee_Vault/   # Obsidian vault (created on init)
```

## Architecture

- **Language**: Python 3.11+
- **File Monitoring**: watchdog library
- **AI Integration**: Anthropic SDK (Claude)
- **Storage**: File-based (markdown with YAML frontmatter)
- **Testing**: pytest

## Success Criteria

- ✅ Detects files within 60 seconds
- ✅ Generates plans in under 10 seconds
- ✅ Processes 10 tasks in under 5 minutes
- ✅ Zero autonomous sensitive actions without approval
- ✅ 24-hour uptime without crashes

## Documentation

- [Specification](specs/001-ai-employee-bronze/spec.md) - Feature requirements
- [Architecture Plan](specs/001-ai-employee-bronze/plan.md) - Technical design
- [Data Model](specs/001-ai-employee-bronze/data-model.md) - Entity schemas
- [Quickstart Guide](specs/001-ai-employee-bronze/quickstart.md) - Detailed setup
- [Tasks](specs/001-ai-employee-bronze/tasks.md) - Implementation tasks

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black ai_employee tests

# Lint code
pylint ai_employee
flake8 ai_employee
```

## Troubleshooting

### "API key not found"
Check that `.env` file exists and contains `ANTHROPIC_API_KEY=sk-ant-...`

### "Permission denied"
Ensure you have read/write permissions for vault and monitored folders

### Files not being detected
Verify the watch folder path and check logs: `tail -f AI_Employee_Vault/activity.log`

## License

[Your license here]

## Version

1.0.0 - Bronze Tier Initial Release
