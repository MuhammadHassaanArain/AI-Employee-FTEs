---
id: 001
title: Create AI Employee Bronze Spec
stage: spec
date: 2026-02-15
surface: agent
model: claude-sonnet-4-5
feature: 001-ai-employee-bronze
branch: 001-ai-employee-bronze
user: Hassaan
command: /sp.specify
labels: ["specification", "ai-employee", "bronze-tier", "obsidian"]
links:
  spec: specs/001-ai-employee-bronze/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-employee-bronze/spec.md
  - specs/001-ai-employee-bronze/checklists/requirements.md
tests:
  - Specification quality validation (all items passed)
---

## Prompt

# Sp.specify.md - Personal AI Employee Bronze Tier

## Objective
Build a foundational Personal AI Employee (Digital FTE) that can monitor a single input source, log tasks in Obsidian, and plan actions via Claude Code.

## Vault Structure
- /Inbox
- /Needs_Action
- /Done
- Dashboard.md
- Company_Handbook.md

## Tasks
1. **Obsidian Vault Setup**
   - Create vault `AI_Employee_Vault`
   - Add `Dashboard.md` with placeholders for recent activity
   - Add `Company_Handbook.md` with basic rules (e.g., "Always flag urgent emails", "Human approval required for payments > $50")

2. **Watcher Script**
   - Choose one source: Gmail or File System
   - For Gmail:
     - Detect unread & important emails
     - Save as `.md` files in `/Needs_Action`
   - For File System:
     - Monitor a folder for new files
     - Copy to `/Needs_Action` with metadata

3. **Claude Code Integration**
   - Read `/Needs_Action` items
   - Create `Plan.md` files in `/Plans` with actionable steps
   - Ensure AI writes to vault correctly
   - Implement basic Agent Skills for reading/writing files

4. **Automation**
   - Basic Ralph Wiggum loop: repeat processing until `/Needs_Action` is empty or max iterations reached

5. **Deliverables**
   - Obsidian Vault with Dashboard.md & Company_Handbook.md
   - One working Watcher script
   - Claude Code agent reading/writing vault
   - Basic folder structure implemented

## Notes
- Keep all files local; do not send sensitive data externally
- Implement simple logging of actions for review
- Ensure AI never executes payments or sensitive actions autonomously

## Response snapshot

Created comprehensive specification for Personal AI Employee Bronze Tier with:
- 4 prioritized user stories (P1: Task capture, P2: AI planning & handbook rules, P3: Autonomous loop)
- 17 functional requirements covering vault setup, file monitoring, Claude Code integration, and safety constraints
- 10 measurable success criteria (technology-agnostic)
- 8 edge cases identified
- Clear scope boundaries (In/Out of scope)
- Dependencies and assumptions documented
- Specification quality checklist created and validated (all items passed)

Branch created: 001-ai-employee-bronze
Spec file: specs/001-ai-employee-bronze/spec.md

## Outcome

- ✅ Impact: Complete, validated specification ready for planning phase. No clarifications needed - all requirements use reasonable defaults.
- 🧪 Tests: Specification quality validation completed - all 12 checklist items passed
- 📁 Files: Created spec.md (14KB) and requirements.md checklist (3KB)
- 🔁 Next prompts: `/sp.plan` to create architectural plan, or `/sp.clarify` if user wants to refine requirements
- 🧠 Reflection: Specification successfully balances completeness with simplicity appropriate for Bronze tier. File system monitoring chosen over Gmail for MVP simplicity. All safety constraints (approval checkpoints, local-only data) clearly defined.

## Evaluation notes (flywheel)

- Failure modes observed: Initial spec created outside bronze-tier directory (corrected by moving specs folder)
- Graders run and results (PASS/FAIL): PASS - All specification quality checklist items validated successfully
- Prompt variant (if applicable): Standard /sp.specify workflow with quality validation
- Next experiment (smallest change to try): Consider adding performance benchmarks to success criteria for future specs
