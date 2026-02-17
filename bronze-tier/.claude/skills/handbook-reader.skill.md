# handbook-reader

Read company handbook rules to guide AI Employee behavior.

## Purpose

This skill allows Claude Code to read the Company Handbook which contains behavioral rules, constraints, and guidelines that must be followed when generating plans. Rules have priority levels (CRITICAL, HIGH, MEDIUM, LOW) that determine their importance.

## When to Use

- Before generating any plan for a task
- When determining if approval checkpoints are needed
- When checking for constraints on specific actions

## Inputs

- **vault_path** (optional): Path to Obsidian vault. Defaults to `./ai_employee_vault`

## Outputs

Returns handbook content including:
- Full text of all rules
- Rule priority levels
- Behavioral guidelines

## Allowed File Operations

- **Read**: Company handbook at `{vault_path}/Company_Handbook.md`

## Handbook Format

Rules follow this format:

```markdown
# Company Handbook

## Rules
- [CRITICAL] Never delete original files.
- [HIGH] Ask for approval before sending emails.
- [MEDIUM] Summaries under 200 words.
- [LOW] Use bullet points when possible.
```

## Example Usage

```
Read the company handbook to understand behavioral rules.
```

## Implementation Notes

- Handbook is read-only and never modified by Claude Code
- Rules with [CRITICAL] or [HIGH] priority must be strictly enforced
- Rules may require adding approval checkpoints to plans
- Handbook can be updated by users; changes apply immediately
- This skill is READ-ONLY
