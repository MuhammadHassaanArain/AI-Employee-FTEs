# Feature Specification: Personal AI Employee Bronze Tier

**Feature Branch**: `001-ai-employee-bronze`
**Created**: 2026-02-15
**Status**: Draft
**Input**: User description: "Build a foundational Personal AI Employee (Digital FTE) that can monitor a single input source, log tasks in Obsidian, and plan actions via Claude Code."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Monitor and Capture Tasks (Priority: P1)

As a user, I want the AI Employee to automatically detect new items from a monitored source and save them as tasks in my Obsidian vault, so I never miss important work items.

**Why this priority**: This is the foundation of the entire system. Without reliable task capture, nothing else matters. This delivers immediate value by automating the manual process of checking for new items and logging them.

**Independent Test**: Can be fully tested by placing a new file in the monitored folder and verifying it appears as a markdown file in the `/Needs_Action` folder with correct metadata. Delivers value by eliminating manual task logging.

**Acceptance Scenarios**:

1. **Given** a monitored folder is empty, **When** a new file is added to the folder, **Then** the watcher detects it within 60 seconds and creates a corresponding `.md` file in `/Needs_Action` with metadata (timestamp, source, file name)
2. **Given** multiple files are added simultaneously, **When** the watcher runs, **Then** all files are captured as separate task files in `/Needs_Action`
3. **Given** the Obsidian vault structure exists, **When** the system starts, **Then** the Dashboard.md displays the count of items in `/Needs_Action`
4. **Given** a task file exists in `/Needs_Action`, **When** I open it in Obsidian, **Then** I can read the full content and metadata in a structured format

---

### User Story 2 - AI-Powered Action Planning (Priority: P2)

As a user, I want Claude Code to analyze tasks in `/Needs_Action` and generate actionable plans, so I have clear next steps for each task without manual planning effort.

**Why this priority**: This adds intelligence to the system. While P1 captures tasks, P2 makes them actionable by providing AI-generated plans. This is the core "employee" behavior that differentiates this from a simple file watcher.

**Independent Test**: Can be tested by manually placing a task file in `/Needs_Action`, running the Claude Code integration, and verifying a `Plan.md` file is created in `/Plans` with actionable steps. Delivers value by providing intelligent task breakdown.

**Acceptance Scenarios**:

1. **Given** a task file exists in `/Needs_Action`, **When** Claude Code processes it, **Then** a corresponding `Plan.md` file is created in `/Plans` with numbered action steps
2. **Given** a task requires human approval (e.g., payment >$50), **When** Claude Code generates the plan, **Then** the plan includes a clear approval checkpoint before any sensitive action
3. **Given** multiple tasks exist in `/Needs_Action`, **When** Claude Code runs, **Then** plans are generated for each task in priority order
4. **Given** a plan is successfully created, **When** the task is processed, **Then** the original task file is moved from `/Needs_Action` to `/Done` with a timestamp

---

### User Story 3 - Autonomous Processing Loop (Priority: P3)

As a user, I want the AI Employee to continuously process tasks until the queue is empty, so the system operates autonomously without constant manual intervention.

**Why this priority**: This makes the system truly autonomous. While P1 and P2 provide the core functionality, P3 enables hands-off operation. This is lower priority because users can manually trigger processing initially.

**Independent Test**: Can be tested by placing multiple tasks in `/Needs_Action`, starting the automation loop, and verifying all tasks are processed sequentially until the folder is empty or max iterations is reached. Delivers value by enabling unattended operation.

**Acceptance Scenarios**:

1. **Given** 5 tasks exist in `/Needs_Action`, **When** the automation loop starts, **Then** all 5 tasks are processed sequentially and moved to `/Done`
2. **Given** the automation loop is running, **When** `/Needs_Action` becomes empty, **Then** the loop completes gracefully and logs the completion
3. **Given** the automation loop has processed 10 tasks, **When** more tasks remain, **Then** the loop stops at the max iteration limit and logs a warning
4. **Given** an error occurs during task processing, **When** the loop encounters it, **Then** the error is logged, the problematic task is flagged, and the loop continues with the next task

---

### User Story 4 - Handbook-Guided Behavior (Priority: P2)

As a user, I want the AI Employee to follow rules defined in `Company_Handbook.md`, so its behavior aligns with my preferences and safety requirements.

**Why this priority**: This ensures safe and predictable operation. The handbook acts as a constraint system that prevents unwanted autonomous actions. Critical for trust and safety.

**Independent Test**: Can be tested by adding a rule to the handbook (e.g., "Flag all emails with 'urgent' in subject"), placing a matching task in `/Needs_Action`, and verifying the plan includes the flagging action. Delivers value by enabling customizable behavior.

**Acceptance Scenarios**:

1. **Given** the handbook contains "Always flag urgent emails", **When** a task with "urgent" in the title is processed, **Then** the generated plan includes a flagging step
2. **Given** the handbook contains "Human approval required for payments >$50", **When** a task involves a $100 payment, **Then** the plan includes an explicit approval checkpoint and does not execute the payment autonomously
3. **Given** the handbook is updated with a new rule, **When** the next task is processed, **Then** the new rule is applied without restarting the system
4. **Given** a task conflicts with a handbook rule, **When** Claude Code processes it, **Then** the plan includes a warning and requests human review

---

### Edge Cases

- What happens when the monitored folder is deleted or becomes inaccessible?
- How does the system handle corrupted or unreadable files in the monitored folder?
- What happens if the Obsidian vault structure is manually modified (folders deleted/renamed)?
- How does the system handle tasks that cannot be parsed or understood by Claude Code?
- What happens if Claude Code is unavailable or returns an error?
- How does the system prevent duplicate task creation if the same file is detected multiple times?
- What happens when `/Needs_Action` contains more tasks than the max iteration limit?
- How does the system handle very large files that exceed reasonable processing limits?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create an Obsidian vault named `AI_Employee_Vault` with the following folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Plans`
- **FR-002**: System MUST create a `Dashboard.md` file that displays the count of items in `/Needs_Action`, recent activity log (last 10 actions), and system status
- **FR-003**: System MUST create a `Company_Handbook.md` file with default rules including "Always flag urgent emails" and "Human approval required for payments >$50"
- **FR-004**: System MUST implement a file system watcher that monitors a designated folder for new files
- **FR-005**: System MUST detect new files within 60 seconds of their creation in the monitored folder
- **FR-006**: System MUST convert detected files into markdown format and save them in `/Needs_Action` with metadata including timestamp, source path, and original filename
- **FR-007**: System MUST provide a mechanism for Claude Code to read files from `/Needs_Action`
- **FR-008**: System MUST enable Claude Code to create `Plan.md` files in `/Plans` with structured action steps
- **FR-009**: System MUST move processed task files from `/Needs_Action` to `/Done` after successful plan creation
- **FR-010**: System MUST implement a processing loop that continues until `/Needs_Action` is empty or a maximum iteration count (default: 10) is reached
- **FR-011**: System MUST log all actions (file detection, plan creation, errors) to a simple text log file with timestamps
- **FR-012**: System MUST read and apply rules from `Company_Handbook.md` when generating plans
- **FR-013**: System MUST prevent autonomous execution of sensitive actions (payments, external communications) without explicit human approval checkpoints in plans
- **FR-014**: System MUST handle errors gracefully by logging them and continuing with the next task rather than crashing
- **FR-015**: System MUST prevent duplicate task creation by tracking processed files
- **FR-016**: System MUST keep all data local and never transmit sensitive information to external services (except Claude Code API for plan generation)
- **FR-017**: System MUST update `Dashboard.md` after each processing cycle with current counts and recent activity

### Key Entities

- **Task**: Represents a work item captured from the monitored source. Contains original content, metadata (timestamp, source, status), and a unique identifier. Stored as markdown files in `/Needs_Action` or `/Done`.
- **Plan**: Represents an AI-generated action plan for a task. Contains numbered steps, approval checkpoints, and references to the source task. Stored as markdown files in `/Plans`.
- **Handbook Rule**: Represents a behavioral constraint or guideline. Contains rule text and priority level. Stored in `Company_Handbook.md`.
- **Activity Log Entry**: Represents a system action. Contains timestamp, action type, affected files, and outcome. Stored in log file and displayed in `Dashboard.md`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully detects and captures 100% of new files placed in the monitored folder within 60 seconds
- **SC-002**: Users can review all captured tasks in Obsidian without needing to check the original source
- **SC-003**: Claude Code generates actionable plans for at least 90% of captured tasks without human intervention
- **SC-004**: System processes a queue of 10 tasks from detection to plan creation in under 5 minutes
- **SC-005**: Zero sensitive actions (payments, external communications) are executed autonomously without explicit approval checkpoints
- **SC-006**: System operates continuously for 24 hours without crashes or requiring manual intervention
- **SC-007**: Users can add or modify handbook rules and see them applied to the next processed task
- **SC-008**: Dashboard provides accurate real-time counts of pending and completed tasks
- **SC-009**: All system actions are logged with timestamps for audit and debugging purposes
- **SC-010**: System handles errors (corrupted files, Claude Code failures) without stopping the processing loop

## Scope & Boundaries *(mandatory)*

### In Scope

- File system monitoring for a single designated folder
- Obsidian vault creation and management
- Task capture and storage in markdown format
- Integration with Claude Code for plan generation
- Basic automation loop with configurable iteration limits
- Simple text-based logging
- Handbook-based rule system
- Dashboard for status visibility

### Out of Scope

- Gmail integration (deferred to Silver/Gold tiers)
- Multi-source monitoring (only one source for Bronze tier)
- Advanced natural language processing beyond Claude Code capabilities
- Task prioritization algorithms (simple FIFO processing)
- User interface beyond Obsidian
- Mobile app or web interface
- Real-time notifications or alerts
- Integration with external task management systems (Jira, Asana, etc.)
- Advanced security features (encryption, access control)
- Multi-user support (single user only)
- Cloud synchronization or backup

## Dependencies & Assumptions *(mandatory)*

### Dependencies

- **Obsidian**: User must have Obsidian installed to view and manage the vault
- **Claude Code**: System requires access to Claude Code API for plan generation
- **File System Access**: System requires read/write permissions to the designated folders
- **Python/Node.js Runtime**: Watcher script requires a runtime environment (specific language to be determined in planning phase)

### Assumptions

- User has basic familiarity with Obsidian and markdown files
- Monitored folder contains text-based files that can be converted to markdown
- Claude Code API is available and responsive (average response time <5 seconds)
- User will manually review and execute plans (no autonomous execution in Bronze tier)
- File system is reliable and accessible (local storage, not network drives)
- Files in monitored folder are reasonably sized (<10MB each)
- User will configure the monitored folder path during initial setup
- Default polling interval of 60 seconds is acceptable for Bronze tier use cases
- Maximum 10 iterations per processing loop is sufficient for typical workloads

## Non-Functional Requirements *(optional)*

### Performance

- File detection latency: <60 seconds from file creation to task capture
- Plan generation: <10 seconds per task (dependent on Claude Code API)
- Dashboard update: <2 seconds after each processing cycle
- System startup: <5 seconds to initialize watcher and vault

### Reliability

- System uptime: 99% over a 24-hour period (allowing for brief restarts)
- Error recovery: System must recover from individual task failures without stopping
- Data integrity: Zero data loss for captured tasks

### Usability

- Setup time: User can configure and start the system in under 10 minutes
- Handbook rules: Written in plain English, no technical syntax required
- Log readability: Logs are human-readable without specialized tools

### Security

- Local data only: No sensitive data transmitted externally except to Claude Code API
- Approval checkpoints: All sensitive actions require explicit human approval
- Log privacy: Logs do not contain sensitive content (passwords, tokens, PII)

## Open Questions *(optional)*

None at this time. All critical decisions have been made with reasonable defaults documented in the Assumptions section.
