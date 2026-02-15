# Research: Personal AI Employee Bronze Tier

**Feature**: 001-ai-employee-bronze
**Date**: 2026-02-15
**Purpose**: Document technology decisions and implementation patterns for Bronze tier AI Employee

## Research Areas

### 1. File System Monitoring

**Question**: Which Python library should we use for cross-platform file system monitoring?

**Options Evaluated**:

| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| watchdog | Cross-platform, event-driven, well-maintained, 10k+ stars | Requires threading | ✅ **Selected** |
| inotify (Linux) | Native, very fast | Linux-only, not cross-platform | ❌ Rejected |
| polling (custom) | Simple, no dependencies | High CPU usage, 60s latency | ❌ Rejected |

**Decision**: Use `watchdog` library with Observer pattern

**Rationale**:
- Cross-platform support (Windows, macOS, Linux) is critical for Bronze tier
- Event-driven architecture provides <1s detection latency (better than 60s requirement)
- Well-documented with extensive examples
- Active maintenance (last update: 2025)
- Simple API: `Observer` + `FileSystemEventHandler`

**Implementation Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TaskFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Process new file
            pass

observer = Observer()
observer.schedule(TaskFileHandler(), path, recursive=False)
observer.start()
```

**Alternatives Considered**:
- `pyinotify`: Linux-only, breaks cross-platform requirement
- Custom polling: Simple but inefficient, doesn't meet responsiveness goals
- `fswatch`: Requires external binary, complicates installation

---

### 2. Claude API Integration

**Question**: How should we structure prompts to include handbook rules and generate structured plans?

**Decision**: Use Anthropic SDK with structured prompt templates and JSON mode for plan generation

**Rationale**:
- Official SDK provides best practices and error handling
- Supports system prompts for handbook rule injection
- JSON mode ensures structured plan output
- Built-in retry logic and rate limit handling

**Prompt Structure**:
```python
system_prompt = f"""You are an AI assistant helping to create action plans for tasks.

Company Handbook Rules:
{handbook_rules}

Your task is to:
1. Analyze the task content
2. Apply relevant handbook rules
3. Generate numbered action steps
4. Add approval checkpoints for sensitive actions (payments >$50, external communications)
5. Return a structured plan in JSON format
"""

user_prompt = f"""Task: {task_title}
Content: {task_content}

Generate an action plan following the handbook rules."""
```

**API Usage Pattern**:
```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    system=system_prompt,
    messages=[{"role": "user", "content": user_prompt}]
)
```

**Error Handling**:
- Retry with exponential backoff (3 attempts)
- Log rate limit errors with wait time
- Fallback: Create basic plan template if API unavailable

**Alternatives Considered**:
- Direct HTTP requests: More complex, no built-in error handling
- LangChain: Over-engineered for Bronze tier needs
- Local LLM: Requires GPU, complicates setup

---

### 3. Markdown File Management

**Question**: How should we handle YAML frontmatter and markdown content for task/plan files?

**Decision**: Use `python-frontmatter` library for parsing and generation

**Rationale**:
- Obsidian-compatible YAML frontmatter support
- Simple API for reading and writing
- Preserves markdown formatting
- Handles metadata serialization automatically

**File Format Standard**:

**Task File** (`/Needs_Action/task-{uuid}.md`):
```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
title: "Review Q4 Budget Report"
source_path: "/monitored/budget_report.pdf"
created_at: "2026-02-15T10:30:00Z"
status: "needs_action"
original_filename: "budget_report.pdf"
file_size: 2048576
detected_at: "2026-02-15T10:30:15Z"
---

# Review Q4 Budget Report

[Original file content or summary]
```

**Plan File** (`/Plans/plan-{task_uuid}.md`):
```markdown
---
id: "660e8400-e29b-41d4-a716-446655440001"
task_id: "550e8400-e29b-41d4-a716-446655440000"
created_at: "2026-02-15T10:31:00Z"
handbook_rules_applied:
  - "Human approval required for payments >$50"
approval_checkpoints: [3]
---

# Action Plan: Review Q4 Budget Report

## Steps

1. Open the budget report file
2. Review revenue and expense sections
3. **[APPROVAL REQUIRED]** If any discrepancies found, prepare correction memo
4. Update financial tracking spreadsheet
5. Archive report in /Done

## Warnings

- This task may involve financial decisions requiring approval
```

**Implementation**:
```python
import frontmatter

# Reading
with open(task_file, 'r') as f:
    post = frontmatter.load(f)
    metadata = post.metadata
    content = post.content

# Writing
post = frontmatter.Post(content, **metadata)
with open(task_file, 'w') as f:
    f.write(frontmatter.dumps(post))
```

**Alternatives Considered**:
- Manual YAML parsing: Error-prone, reinventing the wheel
- JSON files: Not Obsidian-native, less human-readable
- Plain markdown: No structured metadata

---

### 4. Error Handling Patterns

**Question**: How should we handle errors gracefully without stopping the processing loop?

**Decision**: Implement tiered error handling with retry logic and comprehensive logging

**Error Handling Architecture**:

**Tier 1: Recoverable Errors (Retry)**
- Claude API rate limits → Exponential backoff (1s, 2s, 4s)
- Network timeouts → Retry 3 times
- File read errors → Skip file, log warning

**Tier 2: Non-Recoverable Errors (Skip & Log)**
- Corrupted files → Log error, move to `/Errors` folder
- Invalid metadata → Log error, flag for manual review
- Vault structure missing → Attempt auto-repair, log if fails

**Tier 3: Critical Errors (Shutdown)**
- No API key configured → Exit with clear error message
- Vault path inaccessible → Exit with permission guidance
- Python version incompatible → Exit with upgrade instructions

**Implementation Pattern**:
```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def call_claude_api(prompt):
    try:
        response = client.messages.create(...)
        return response
    except anthropic.RateLimitError as e:
        logger.warning(f"Rate limit hit, retrying: {e}")
        raise
    except anthropic.APIError as e:
        logger.error(f"API error: {e}")
        raise

def process_task(task_file):
    try:
        task = load_task(task_file)
        plan = call_claude_api(task)
        save_plan(plan)
    except Exception as e:
        logger.error(f"Failed to process {task_file}: {e}")
        # Continue with next task
        return None
```

**Logging Strategy**:
- Use Python `logging` module with file handler
- Log levels: DEBUG (development), INFO (operations), WARNING (recoverable), ERROR (failures)
- Log format: `[timestamp] [level] [module] message`
- Separate log file: `activity.log` in vault root

**Alternatives Considered**:
- Fail-fast approach: Too fragile for autonomous operation
- Silent failures: Poor observability
- Email notifications: Over-engineered for Bronze tier

---

### 5. Configuration Management

**Question**: How should users configure API keys, paths, and behavior?

**Decision**: Hybrid approach using `.env` for secrets and CLI arguments for runtime options

**Configuration Schema**:

**.env file** (secrets and defaults):
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (with defaults)
VAULT_PATH=./AI_Employee_Vault
WATCH_FOLDER=./monitored
MAX_ITERATIONS=10
POLL_INTERVAL=60
LOG_LEVEL=INFO
```

**CLI Arguments** (runtime overrides):
```bash
python -m ai_employee run \
  --vault-path ./custom_vault \
  --watch-folder ./inbox \
  --max-iterations 20 \
  --log-level DEBUG
```

**Implementation**:
```python
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--vault-path', default=os.getenv('VAULT_PATH', './AI_Employee_Vault'))
parser.add_argument('--watch-folder', default=os.getenv('WATCH_FOLDER', './monitored'))
parser.add_argument('--max-iterations', type=int, default=int(os.getenv('MAX_ITERATIONS', '10')))
args = parser.parse_args()
```

**Configuration Validation**:
- Check API key exists on startup
- Validate paths are accessible
- Provide clear error messages for missing config
- Create `.env.example` template for users

**Alternatives Considered**:
- Config file (YAML/JSON): More complex, overkill for Bronze tier
- Environment variables only: Less user-friendly for paths
- CLI arguments only: Insecure for API keys

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.11+ | Cross-platform, rich ecosystem, easy deployment |
| File Watching | watchdog | 4.0+ | Event-driven, cross-platform, well-maintained |
| AI Integration | anthropic | 0.18+ | Official SDK, best practices, error handling |
| Markdown Parsing | python-frontmatter | 1.0+ | YAML frontmatter support, Obsidian-compatible |
| Configuration | python-dotenv | 1.0+ | Standard .env file handling |
| Retry Logic | tenacity | 8.2+ | Declarative retry patterns, exponential backoff |
| Testing | pytest | 8.0+ | Industry standard, rich plugin ecosystem |
| Logging | logging (stdlib) | - | Built-in, sufficient for Bronze tier needs |

## Dependencies

**requirements.txt**:
```
anthropic>=0.18.0
watchdog>=4.0.0
python-frontmatter>=1.0.0
python-dotenv>=1.0.0
tenacity>=8.2.0
pyyaml>=6.0.0
pytest>=8.0.0
pytest-mock>=3.12.0
```

## Best Practices Applied

1. **Separation of Concerns**: Watcher, processor, and Claude client are independent modules
2. **Fail-Safe Defaults**: System continues operating even with partial failures
3. **Comprehensive Logging**: All operations logged for debugging and audit
4. **Configuration Flexibility**: Sensible defaults with override capability
5. **Cross-Platform**: No OS-specific dependencies or assumptions
6. **Security**: API keys in .env, never committed to git
7. **Testability**: All modules designed for unit testing with mocks

## Implementation Priorities

**Phase 0 Complete** ✅

Next: Phase 1 (Design & Contracts)
- Create data-model.md with detailed entity schemas
- Generate contract files in contracts/ directory
- Write quickstart.md for user onboarding
- Update agent context with technology stack
