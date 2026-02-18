# Implementation Plan: Personal AI Employee Bronze Tier

**Branch**: `001-ai-employee-bronze` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-ai-employee-bronze/spec.md`

## Summary

Build a foundational Personal AI Employee that monitors a file system folder, captures new files as tasks in an Obsidian vault, and uses Claude Code API to generate actionable plans. The system operates autonomously with configurable iteration limits and enforces safety rules from a Company Handbook.

**Technical Approach**: Python-based CLI tool using watchdog for file monitoring, Anthropic SDK for Claude API integration, and markdown files for all data storage. Simple polling architecture with graceful error handling and comprehensive logging.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `watchdog` (file system monitoring)
- `anthropic` (Claude API client)
- `python-dotenv` (configuration management)
- `pyyaml` (metadata parsing)

**Storage**: File-based (markdown files in Obsidian vault structure)
**Testing**: pytest with fixtures for file system mocking
**Target Platform**: Cross-platform (Windows, macOS, Linux) - local execution
**Project Type**: Single CLI application
**Performance Goals**:
- File detection within 60 seconds
- Plan generation <10 seconds per task
- Dashboard updates <2 seconds
- Support 10 concurrent tasks per processing cycle

**Constraints**:
- Local-only execution (no cloud deployment)
- Single-threaded processing (simplicity over concurrency)
- No database (file-based storage only)
- Human approval required for sensitive actions

**Scale/Scope**:
- Single user
- ~100 tasks per day expected
- Vault size <1GB
- 10 max iterations per processing loop

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file contains only template placeholders. Proceeding with standard software engineering best practices:

✅ **Simplicity**: Single Python project, no unnecessary abstractions
✅ **Testability**: pytest-based testing with clear unit/integration boundaries
✅ **Observability**: Comprehensive logging to activity.log with timestamps
✅ **Safety**: Explicit approval checkpoints for sensitive actions
✅ **Modularity**: Clear separation between watcher, processor, and Claude integration

**No violations detected** - architecture aligns with simplicity and testability principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-employee-bronze/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions and patterns
├── data-model.md        # Phase 1: Task/Plan/Log data structures
├── quickstart.md        # Phase 1: Setup and usage guide
├── contracts/           # Phase 1: Claude API contracts and schemas
│   ├── task-schema.yaml
│   ├── plan-schema.yaml
│   └── handbook-schema.yaml
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
ai_employee/
├── __init__.py
├── __main__.py          # CLI entry point
├── config.py            # Configuration management
├── vault/
│   ├── __init__.py
│   ├── manager.py       # Vault initialization and structure
│   └── dashboard.py     # Dashboard.md updates
├── watcher/
│   ├── __init__.py
│   ├── file_watcher.py  # File system monitoring
│   └── task_creator.py  # Convert files to task markdown
├── processor/
│   ├── __init__.py
│   ├── task_processor.py    # Main processing loop
│   ├── claude_client.py     # Claude API integration
│   └── handbook_parser.py   # Parse and apply handbook rules
├── models/
│   ├── __init__.py
│   ├── task.py          # Task data structure
│   ├── plan.py          # Plan data structure
│   └── log_entry.py     # Activity log entry
└── utils/
    ├── __init__.py
    ├── logger.py        # Logging utilities
    └── file_tracker.py  # Duplicate detection

tests/
├── unit/
│   ├── test_vault_manager.py
│   ├── test_file_watcher.py
│   ├── test_task_creator.py
│   ├── test_task_processor.py
│   ├── test_claude_client.py
│   ├── test_handbook_parser.py
│   └── test_models.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_vault_operations.py
└── fixtures/
    ├── sample_tasks/
    ├── sample_handbook.md
    └── mock_responses.json

# Root level files
.env.example             # Configuration template
requirements.txt         # Python dependencies
setup.py                 # Package installation
README.md                # Project overview
```

**Structure Decision**: Single Python project structure chosen because:
- Bronze tier is a standalone CLI tool (no web/mobile components)
- All functionality is cohesive (file monitoring → task processing → plan generation)
- Simple deployment model (single pip install)
- Clear module boundaries without over-engineering

## Complexity Tracking

**No violations to justify** - architecture follows simplicity principles with no unnecessary complexity.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **File System Monitoring**
   - Research: Python file watching libraries (watchdog vs inotify vs polling)
   - Decision criteria: Cross-platform support, reliability, ease of use
   - Output: Recommended library with usage patterns

2. **Claude API Integration**
   - Research: Anthropic SDK best practices for prompt engineering
   - Decision criteria: Handbook rule injection, plan formatting, error handling
   - Output: Prompt templates and API usage patterns

3. **Markdown File Management**
   - Research: Python markdown libraries and YAML frontmatter handling
   - Decision criteria: Metadata parsing, file generation, Obsidian compatibility
   - Output: File format standards and parsing approach

4. **Error Handling Patterns**
   - Research: Graceful degradation strategies for file system and API errors
   - Decision criteria: Retry logic, logging, user notification
   - Output: Error handling architecture

5. **Configuration Management**
   - Research: Best practices for CLI configuration (env vars, config files, CLI args)
   - Decision criteria: User-friendliness, security (API keys), flexibility
   - Output: Configuration schema and loading strategy

### Expected Outputs (research.md)

- **File Watcher**: watchdog library with Observer pattern
- **Claude Integration**: Anthropic SDK with structured prompts
- **Markdown Handling**: python-frontmatter for YAML + markdown parsing
- **Error Strategy**: Retry with exponential backoff, comprehensive logging
- **Config**: python-dotenv for .env files + CLI args via argparse

## Phase 1: Design & Contracts

### Data Model (data-model.md)

**Task Entity**:
```yaml
id: string (UUID)
title: string
content: string (original file content)
source_path: string
created_at: datetime
status: enum [needs_action, processing, done, error]
metadata:
  original_filename: string
  file_size: int
  detected_at: datetime
```

**Plan Entity**:
```yaml
id: string (UUID)
task_id: string (reference to Task)
steps: list[string]
approval_checkpoints: list[int] (step indices requiring approval)
warnings: list[string]
created_at: datetime
handbook_rules_applied: list[string]
```

**Handbook Rule Entity**:
```yaml
rule_text: string
priority: enum [critical, high, medium, low]
keywords: list[string] (for matching)
action: enum [flag, require_approval, warn, block]
```

**Activity Log Entry**:
```yaml
timestamp: datetime
action_type: enum [file_detected, task_created, plan_generated, error, warning]
task_id: string (optional)
details: string
outcome: enum [success, failure, skipped]
```

### API Contracts (contracts/)

**task-schema.yaml**: Markdown frontmatter format for task files
**plan-schema.yaml**: Markdown frontmatter format for plan files
**handbook-schema.yaml**: Structure for Company_Handbook.md rules
**claude-prompt-template.md**: Template for Claude API prompts with handbook injection

### Quickstart Guide (quickstart.md)

1. Installation: `pip install -e .`
2. Configuration: Copy `.env.example` to `.env`, add Claude API key
3. Initialize vault: `python -m ai_employee init --vault-path ./AI_Employee_Vault`
4. Configure watcher: `python -m ai_employee config --watch-folder ./monitored`
5. Start processing: `python -m ai_employee run`
6. View dashboard: Open `AI_Employee_Vault/Dashboard.md` in Obsidian

## Phase 2: Implementation Phases (High-Level)

**Note**: Detailed tasks will be generated by `/sp.tasks` command. This section provides high-level implementation phases.

### Phase 2.1: Foundation (P1)
- Vault initialization and structure creation
- Configuration management
- Basic logging infrastructure
- Data models (Task, Plan, LogEntry)

### Phase 2.2: File Watching (P1)
- File system watcher implementation
- Task file creation with metadata
- Duplicate detection
- Dashboard updates for task counts

### Phase 2.3: Claude Integration (P2)
- Claude API client setup
- Prompt engineering with handbook injection
- Plan generation and file creation
- Error handling and retries

### Phase 2.4: Processing Loop (P3)
- Main processing loop with iteration limits
- Task queue management
- Graceful shutdown
- Comprehensive error recovery

### Phase 2.5: Handbook System (P2)
- Handbook parser
- Rule matching engine
- Approval checkpoint injection
- Rule application logging

### Phase 2.6: Testing & Polish (P3)
- Unit tests for all modules
- Integration tests for end-to-end flows
- Error scenario testing
- Documentation and README

## Key Architectural Decisions

### 1. File-Based Storage vs Database
**Decision**: File-based storage (markdown files)
**Rationale**:
- Obsidian native format
- Human-readable and editable
- No database setup complexity
- Aligns with Bronze tier simplicity
**Trade-off**: Limited query capabilities, but acceptable for expected scale

### 2. Polling vs Event-Driven File Watching
**Decision**: Event-driven with watchdog library
**Rationale**:
- More responsive than 60-second polling
- Lower CPU usage
- Cross-platform support
**Trade-off**: Slightly more complex than polling, but well-supported library

### 3. Synchronous vs Asynchronous Processing
**Decision**: Synchronous (single-threaded)
**Rationale**:
- Simpler error handling
- Easier debugging
- Sufficient for Bronze tier scale (10 tasks/cycle)
**Trade-off**: Lower throughput, but acceptable for target workload

### 4. Claude API Direct vs Abstraction Layer
**Decision**: Thin wrapper around Anthropic SDK
**Rationale**:
- Avoid premature abstraction
- Direct access to SDK features
- Easier to debug API issues
**Trade-off**: Tighter coupling, but acceptable for single AI provider

### 5. Configuration: Files vs CLI Args vs Environment
**Decision**: Hybrid approach (.env for secrets, CLI args for runtime options)
**Rationale**:
- .env for API keys (security)
- CLI args for paths and behavior (flexibility)
- Sensible defaults for Bronze tier
**Trade-off**: Multiple config sources, but standard pattern

## Risk Analysis & Mitigation

### Risk 1: Claude API Rate Limits
**Impact**: Processing delays or failures
**Mitigation**:
- Implement exponential backoff
- Queue tasks for retry
- Log rate limit errors clearly
**Monitoring**: Track API response times and error rates in logs

### Risk 2: File System Permissions
**Impact**: Cannot read monitored folder or write to vault
**Mitigation**:
- Check permissions on startup
- Provide clear error messages
- Document required permissions in quickstart
**Monitoring**: Log permission errors with actionable guidance

### Risk 3: Corrupted or Malformed Files
**Impact**: Task creation failures
**Mitigation**:
- Validate file readability before processing
- Skip unreadable files with logging
- Continue processing remaining files
**Monitoring**: Track skipped files in activity log

### Risk 4: Handbook Rule Conflicts
**Impact**: Unclear behavior when multiple rules apply
**Mitigation**:
- Define rule priority system
- Apply most restrictive rule when conflicts occur
- Log all applied rules for transparency
**Monitoring**: Log rule conflicts and resolution

### Risk 5: Vault Structure Corruption
**Impact**: System cannot operate
**Mitigation**:
- Validate vault structure on startup
- Auto-repair missing folders
- Backup critical files (Dashboard, Handbook)
**Monitoring**: Log structure validation results

## Success Metrics Mapping

| Success Criterion | Implementation Component | Verification Method |
|-------------------|-------------------------|---------------------|
| SC-001: 100% file detection <60s | watchdog Observer | Integration test with timed file creation |
| SC-002: Review tasks in Obsidian | Markdown file format | Manual verification + schema validation |
| SC-003: 90% plan generation | Claude client + error handling | Track success rate in logs |
| SC-004: 10 tasks in <5 minutes | Processing loop performance | Performance test with 10 sample tasks |
| SC-005: Zero autonomous sensitive actions | Handbook parser + approval checkpoints | Unit tests for checkpoint injection |
| SC-006: 24-hour uptime | Error recovery + graceful degradation | Long-running integration test |
| SC-007: Handbook rule application | Handbook parser + hot reload | Integration test with rule updates |
| SC-008: Accurate dashboard counts | Dashboard updater | Unit tests for count calculations |
| SC-009: Timestamped logging | Logger utility | Log format validation tests |
| SC-010: Error handling without crashes | Try-catch blocks + error recovery | Error scenario integration tests |

## Next Steps

1. **Run `/sp.tasks`** to generate detailed implementation tasks from this plan
2. **Phase 0 Research**: Create `research.md` with technology decisions
3. **Phase 1 Design**: Create `data-model.md`, `contracts/`, and `quickstart.md`
4. **Phase 2 Implementation**: Execute tasks in priority order (P1 → P2 → P3)

## Open Questions for Implementation

1. **Handbook Rule Syntax**: Should rules use regex patterns or simple keyword matching?
   - Recommendation: Start with keyword matching, add regex in Silver tier

2. **Plan File Naming**: Use task ID or sequential numbering?
   - Recommendation: Use task ID for traceability (e.g., `plan-{task_id}.md`)

3. **Dashboard Update Frequency**: Real-time or batch updates?
   - Recommendation: Batch updates after each processing cycle (simpler)

4. **Error Notification**: Log-only or also update Dashboard with errors?
   - Recommendation: Both - log details, Dashboard shows error count

5. **Vault Location**: Fixed path or configurable?
   - Recommendation: Configurable via CLI arg with default `./AI_Employee_Vault`
