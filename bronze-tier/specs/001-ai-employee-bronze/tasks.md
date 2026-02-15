# Tasks: Personal AI Employee Bronze Tier

**Input**: Design documents from `specs/001-ai-employee-bronze/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `ai_employee/` for source, `tests/` for tests
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: ai_employee/, tests/, specs/
- [ ] T002 Initialize Python project with setup.py and requirements.txt
- [ ] T003 [P] Create .env.example with ANTHROPIC_API_KEY, VAULT_PATH, WATCH_FOLDER, MAX_ITERATIONS, LOG_LEVEL
- [ ] T004 [P] Create .gitignore with .env, venv/, __pycache__/, *.pyc, .pytest_cache/
- [ ] T005 [P] Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create ai_employee/__init__.py and ai_employee/__main__.py for CLI entry point
- [ ] T007 Implement configuration management in ai_employee/config.py (load .env, parse CLI args)
- [ ] T008 [P] Create ai_employee/models/__init__.py module
- [ ] T009 [P] Create ai_employee/vault/__init__.py module
- [ ] T010 [P] Create ai_employee/watcher/__init__.py module
- [ ] T011 [P] Create ai_employee/processor/__init__.py module
- [ ] T012 [P] Create ai_employee/utils/__init__.py module
- [ ] T013 Implement logging infrastructure in ai_employee/utils/logger.py (file handler, formatters)
- [ ] T014 Create data models: ai_employee/models/task.py with Task class (id, title, source_path, created_at, status, metadata)
- [ ] T015 [P] Create data models: ai_employee/models/plan.py with Plan class (id, task_id, steps, approval_checkpoints, handbook_rules_applied)
- [ ] T016 [P] Create data models: ai_employee/models/log_entry.py with LogEntry class (timestamp, action_type, task_id, details, outcome)
- [ ] T017 Implement vault manager in ai_employee/vault/manager.py (create_vault, validate_structure, get_paths)
- [ ] T018 Create CLI command: python -m ai_employee init --vault-path PATH (calls vault manager)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Monitor and Capture Tasks (Priority: P1) 🎯 MVP

**Goal**: Automatically detect new files in monitored folder and save as tasks in Obsidian vault

**Independent Test**: Place a file in monitored folder, verify task appears in /Needs_Action with correct metadata within 60 seconds

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement file tracker in ai_employee/utils/file_tracker.py (track processed files, prevent duplicates using JSON)
- [ ] T020 [P] [US1] Implement task creator in ai_employee/watcher/task_creator.py (convert file to markdown with YAML frontmatter)
- [ ] T021 [US1] Implement file watcher in ai_employee/watcher/file_watcher.py (watchdog Observer, FileSystemEventHandler, on_created event)
- [ ] T022 [US1] Integrate file watcher with task creator (detect file → create task → log action)
- [ ] T023 [US1] Implement dashboard updater in ai_employee/vault/dashboard.py (update_counts, add_activity_entry, render_dashboard)
- [ ] T024 [US1] Add dashboard update to task creation flow (increment Needs Action count)
- [ ] T025 [US1] Create CLI command: python -m ai_employee run --watch-folder PATH (start file watcher)
- [ ] T026 [US1] Add graceful shutdown handling (Ctrl+C stops watcher cleanly)

**Checkpoint**: At this point, User Story 1 should be fully functional - files are detected and converted to tasks

---

## Phase 4: User Story 4 - Handbook-Guided Behavior (Priority: P2)

**Goal**: Parse Company_Handbook.md and apply rules when generating plans

**Independent Test**: Add rule to handbook, create task matching keywords, verify rule is applied in plan generation

**Note**: Implementing this before US2 because US2 (plan generation) depends on handbook parsing

### Implementation for User Story 4

- [ ] T027 [P] [US4] Create default Company_Handbook.md template in ai_employee/vault/manager.py (Critical/High/Medium/Low rules)
- [ ] T028 [US4] Implement handbook parser in ai_employee/processor/handbook_parser.py (parse_handbook, extract rules with keywords/actions/priority)
- [ ] T029 [US4] Implement rule matching in ai_employee/processor/handbook_parser.py (match_rules, apply_most_restrictive)
- [ ] T030 [US4] Add handbook hot-reload detection (watch Company_Handbook.md for changes, reload rules)
- [ ] T031 [US4] Add handbook validation on system startup (check structure, log errors if malformed)

**Checkpoint**: Handbook system ready - rules can be parsed and matched against task content

---

## Phase 5: User Story 2 - AI-Powered Action Planning (Priority: P2)

**Goal**: Use Claude to analyze tasks and generate actionable plans with approval checkpoints

**Independent Test**: Manually place task in /Needs_Action, run processor, verify plan created in /Plans with steps and handbook rules applied

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement Claude client in ai_employee/processor/claude_client.py (initialize Anthropic SDK, handle API key)
- [ ] T033 [US2] Create prompt templates in ai_employee/processor/claude_client.py (system prompt with handbook rules, user prompt with task)
- [ ] T034 [US2] Implement plan generation in ai_employee/processor/claude_client.py (call Claude API, parse JSON response, create Plan object)
- [ ] T035 [US2] Add retry logic with exponential backoff in ai_employee/processor/claude_client.py (use tenacity, 3 attempts, 1s-10s wait)
- [ ] T036 [US2] Implement error handling for Claude API (rate limits, timeouts, invalid responses)
- [ ] T037 [US2] Integrate handbook parser with Claude client (inject rules into system prompt, track applied rules)
- [ ] T038 [US2] Implement plan file writer (save Plan object as markdown with YAML frontmatter in /Plans)
- [ ] T039 [US2] Add approval checkpoint markers in plan content (**[APPROVAL REQUIRED]** at specified indices)
- [ ] T040 [US2] Implement task processor in ai_employee/processor/task_processor.py (read /Needs_Action, generate plan, move to /Done)
- [ ] T041 [US2] Add task status updates (needs_action → processing → done)
- [ ] T042 [US2] Update dashboard after plan generation (decrement Needs Action, increment Completed)
- [ ] T043 [US2] Log all plan generation attempts (success, failure, API errors)

**Checkpoint**: Plan generation working - tasks are analyzed and actionable plans are created

---

## Phase 6: User Story 3 - Autonomous Processing Loop (Priority: P3)

**Goal**: Continuously process tasks until queue is empty or max iterations reached

**Independent Test**: Place 5 tasks in /Needs_Action, start loop, verify all processed sequentially and moved to /Done

### Implementation for User Story 3

- [ ] T044 [US3] Implement processing loop in ai_employee/processor/task_processor.py (iterate until /Needs_Action empty or max iterations)
- [ ] T045 [US3] Add iteration counter and max limit check (default 10, configurable via CLI)
- [ ] T046 [US3] Implement error recovery in loop (catch exceptions, log error, continue with next task)
- [ ] T047 [US3] Add loop completion logging (success message when queue empty, warning when max iterations reached)
- [ ] T048 [US3] Update dashboard after each loop iteration (current counts, recent activity)
- [ ] T049 [US3] Add loop status to dashboard (Running/Idle/Error)
- [ ] T050 [US3] Integrate loop with file watcher (watcher detects → loop processes → repeat)

**Checkpoint**: All user stories should now be independently functional - system operates autonomously

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Testing, documentation, and improvements that affect multiple user stories

### Testing

- [ ] T051 [P] Create tests/unit/test_vault_manager.py (test vault creation, structure validation)
- [ ] T052 [P] Create tests/unit/test_file_watcher.py (test file detection with mocked filesystem)
- [ ] T053 [P] Create tests/unit/test_task_creator.py (test markdown generation, metadata formatting)
- [ ] T054 [P] Create tests/unit/test_claude_client.py (test prompt generation, response parsing with mocked API)
- [ ] T055 [P] Create tests/unit/test_handbook_parser.py (test rule parsing, keyword matching, conflict resolution)
- [ ] T056 [P] Create tests/unit/test_task_processor.py (test loop logic, error handling)
- [ ] T057 [P] Create tests/unit/test_models.py (test Task, Plan, LogEntry data classes)
- [ ] T058 Create tests/integration/test_end_to_end.py (test full workflow: file → task → plan → done)
- [ ] T059 [P] Create tests/integration/test_vault_operations.py (test vault creation, file operations)
- [ ] T060 Create tests/fixtures/ directory with sample_tasks/, sample_handbook.md, mock_responses.json
- [ ] T061 Run all tests with pytest and verify 100% pass rate

### Documentation

- [ ] T062 [P] Update README.md with complete setup instructions, usage examples, troubleshooting
- [ ] T063 [P] Verify quickstart.md accuracy (test all commands, update if needed)
- [ ] T064 [P] Add inline code documentation (docstrings for all classes and functions)
- [ ] T065 [P] Create CONTRIBUTING.md with development guidelines

### Performance & Validation

- [ ] T066 Performance test: Verify 10 tasks processed in under 5 minutes
- [ ] T067 Performance test: Verify file detection latency <60 seconds
- [ ] T068 Performance test: Verify plan generation <10 seconds per task
- [ ] T069 Performance test: Verify dashboard update <2 seconds
- [ ] T070 Validate all success criteria SC-001 through SC-010 from spec.md
- [ ] T071 Test edge cases: missing folder, corrupted files, API failures, vault structure corruption
- [ ] T072 Run 24-hour stability test (verify system operates without crashes)

### Code Quality

- [ ] T073 [P] Add type hints to all functions and classes
- [ ] T074 [P] Run linter (pylint/flake8) and fix all warnings
- [ ] T075 [P] Run formatter (black) on all Python files
- [ ] T076 Code review: Check for security issues (API key handling, file permissions)
- [ ] T077 Code review: Verify error messages are user-friendly and actionable

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - No dependencies on other stories
- **User Story 4 (Phase 4)**: Depends on Foundational - No dependencies on other stories
- **User Story 2 (Phase 5)**: Depends on Foundational AND User Story 4 (needs handbook parser)
- **User Story 3 (Phase 6)**: Depends on Foundational, US1, US2 (needs file watcher and plan generation)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
    ├─→ User Story 1 (P1) - Monitor and Capture [Independent]
    ├─→ User Story 4 (P2) - Handbook Rules [Independent]
    │       ↓
    └─→ User Story 2 (P2) - AI Planning [Depends on US4]
            ↓
        User Story 3 (P3) - Autonomous Loop [Depends on US1 + US2]
```

### Within Each User Story

- **US1**: File tracker and task creator can be built in parallel → integrate with watcher → add dashboard updates
- **US4**: Handbook template and parser can be built together → add validation and hot-reload
- **US2**: Claude client and prompt templates in parallel → integrate with handbook → add to processor
- **US3**: Build on top of existing processor → add loop logic and error recovery

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel

**Phase 2 (Foundational)**: T008-T012 (module creation) can run in parallel, T014-T016 (models) can run in parallel

**Phase 3 (US1)**: T019, T020 can run in parallel

**Phase 4 (US4)**: T027 can run in parallel with T028

**Phase 5 (US2)**: T032, T033 can run in parallel

**Phase 7 (Testing)**: T051-T057 (unit tests) can all run in parallel, T062-T065 (docs) can run in parallel, T073-T075 (code quality) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch file tracker and task creator together:
Task T019: "Implement file tracker in ai_employee/utils/file_tracker.py"
Task T020: "Implement task creator in ai_employee/watcher/task_creator.py"

# Then integrate:
Task T021: "Implement file watcher (uses T019 and T020)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T018) - CRITICAL
3. Complete Phase 3: User Story 1 (T019-T026)
4. **STOP and VALIDATE**: Test file detection and task creation independently
5. Deploy/demo if ready

**Result**: Working file monitoring system that captures tasks in Obsidian vault

### Incremental Delivery

1. **Foundation** (Phases 1-2): Project structure and core infrastructure → Foundation ready
2. **MVP** (Phase 3): Add User Story 1 → Test independently → Deploy/Demo (file monitoring works!)
3. **Intelligence** (Phases 4-5): Add US4 + US2 → Test independently → Deploy/Demo (AI planning works!)
4. **Automation** (Phase 6): Add US3 → Test independently → Deploy/Demo (autonomous operation works!)
5. **Polish** (Phase 7): Testing and documentation → Production ready

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational (Phases 1-2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Phase 3)
   - Developer B: User Story 4 (Phase 4)
3. **After US4 complete**:
   - Developer A: User Story 2 (Phase 5) - needs US4
   - Developer B: Start testing (Phase 7)
4. **After US1 + US2 complete**:
   - Developer A: User Story 3 (Phase 6)
   - Developer B: Continue testing and docs

---

## Task Summary

**Total Tasks**: 77

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 13 tasks
- Phase 3 (US1 - Monitor): 8 tasks
- Phase 4 (US4 - Handbook): 5 tasks
- Phase 5 (US2 - Planning): 12 tasks
- Phase 6 (US3 - Loop): 7 tasks
- Phase 7 (Polish): 27 tasks

**By User Story**:
- US1 (Monitor and Capture): 8 tasks
- US2 (AI Planning): 12 tasks
- US3 (Autonomous Loop): 7 tasks
- US4 (Handbook Rules): 5 tasks
- Infrastructure: 18 tasks
- Testing & Polish: 27 tasks

**Parallel Opportunities**: 28 tasks marked [P] can run in parallel with other tasks

**MVP Scope**: Phases 1-3 (26 tasks) delivers working file monitoring system

---

## Success Criteria Mapping

| Success Criterion | Implementation Tasks | Verification Method |
|-------------------|---------------------|---------------------|
| SC-001: 100% file detection <60s | T019-T026 (US1) | T067 performance test |
| SC-002: Review tasks in Obsidian | T020, T024 (US1) | Manual verification with Obsidian |
| SC-003: 90% plan generation | T032-T043 (US2) | T058 integration test |
| SC-004: 10 tasks in <5 minutes | T044-T050 (US3) | T066 performance test |
| SC-005: Zero autonomous sensitive actions | T027-T031, T037-T039 (US4, US2) | T054, T055 unit tests |
| SC-006: 24-hour uptime | T044-T047 (US3) | T072 stability test |
| SC-007: Handbook rule application | T027-T031 (US4) | T055 unit test |
| SC-008: Accurate dashboard counts | T023-T024, T042, T048 | T059 integration test |
| SC-009: Timestamped logging | T013 (Foundational) | T051 unit test |
| SC-010: Error handling without crashes | T046-T047 (US3) | T071 edge case tests |

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **Commit strategy**: Commit after each task or logical group
- **Validation**: Stop at any checkpoint to validate story independently
- **Tests**: Included in Polish phase (not TDD approach for Bronze tier)
- **File paths**: All paths are exact and implementation-ready
- **Dependencies**: Clearly documented to avoid blocking issues

---

## Next Steps

1. **Start with MVP**: Complete Phases 1-3 (T001-T026) for working file monitoring
2. **Validate MVP**: Test User Story 1 independently before proceeding
3. **Add Intelligence**: Complete Phases 4-5 (T027-T043) for AI planning
4. **Add Automation**: Complete Phase 6 (T044-T050) for autonomous operation
5. **Polish**: Complete Phase 7 (T051-T077) for production readiness
