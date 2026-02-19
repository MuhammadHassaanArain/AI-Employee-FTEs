# Claude Code Integration Guide - Silver Tier

## Two Modes of Operation

Silver Tier supports **two modes** for task processing:

### Mode 1: Automated Mode (Rule-Based)
- Uses pattern matching in `reasoning_skill.py`
- Fast, deterministic responses
- No Claude API calls needed
- Good for: Automation, scheduling, demos

**Command:**
```bash
python claude_runner.py
```

### Mode 2: Claude Code Mode (Real AI)
- Uses Claude Code for intelligent reasoning
- Real AI analysis and planning
- Context-aware decisions
- Good for: Complex tasks, real work, quality output

**Command:**
```bash
# Run inside Claude Code CLI
python claude_runner_with_ai.py
```

---

## How to Use Claude Code Mode (Real AI Reasoning)

### Step 1: Start Claude Code CLI

```bash
# Open Claude Code CLI
claude

# Or if using the CLI directly
claude code
```

### Step 2: Navigate to Silver Tier

```bash
cd D:\Hassaan_Work\GIAIC\Quarter-04\Hackathons\hackathon-0\AI-Employee-FTEs\silver-tier
```

### Step 3: Create a Task

```bash
# Create a test task
echo "Research the top 3 AI automation platforms in 2026. Compare features, pricing, and use cases. Create a summary report." > ai_employee_vault/Inbox/research-task.txt
```

### Step 4: Run Claude Code Runner

```bash
# Inside Claude Code CLI
python claude_runner_with_ai.py
```

### Step 5: Claude Code Processes the Task

Claude Code will:
1. Read the task file
2. Read the Company Handbook
3. Use AI reasoning to analyze the task
4. Generate an intelligent, contextual plan
5. Determine if approval is needed
6. Write the plan to Plans/ folder
7. Move the task appropriately

### Step 6: Check Results

```bash
# View generated plan
cat ai_employee_vault/Plans/plan-*.md

# Check task location
ls ai_employee_vault/Done/          # If no approval needed
ls ai_employee_vault/Waiting_Approval/  # If approval needed
```

---

## Comparison: Automated vs Claude Code Mode

| Feature | Automated Mode | Claude Code Mode |
|---------|---------------|------------------|
| **Reasoning** | Pattern matching | Real AI reasoning |
| **Speed** | Fast (< 1 sec) | Slower (5-10 sec) |
| **Quality** | Good for simple tasks | Excellent for complex tasks |
| **Context** | Rule-based | Fully contextual |
| **API Calls** | None | Uses Claude API |
| **Best For** | Automation, demos | Real work, quality |

---

## When to Use Each Mode

### Use Automated Mode When:
- Running scheduled tasks (Task Scheduler)
- Need fast processing
- Tasks are straightforward
- Demonstrating the system
- No Claude API access

### Use Claude Code Mode When:
- Tasks are complex or nuanced
- Need high-quality reasoning
- Want context-aware plans
- Working on important tasks
- Have Claude API access

---

## Example Workflows

### Automated Mode Workflow

```bash
# 1. Create tasks
echo "Research AI tools" > ai_employee_vault/Inbox/task1.txt
echo "Send email to client@example.com" > ai_employee_vault/Inbox/task2.txt

# 2. Run automated processing
python claude_runner.py

# 3. Check results
ls ai_employee_vault/Done/
ls ai_employee_vault/Waiting_Approval/
```

**Result:**
- Research task → Done/ (pattern matched as "research")
- Email task → Waiting_Approval/ (pattern matched as "email")

### Claude Code Mode Workflow

```bash
# 1. Start Claude Code CLI
claude

# 2. Navigate to silver-tier
cd silver-tier

# 3. Create a complex task
cat > ai_employee_vault/Inbox/complex-task.txt << 'EOF'
Analyze our Q1 2026 performance data and create a comprehensive report.
Include:
- Revenue trends
- Customer acquisition metrics
- Product performance analysis
- Recommendations for Q2

The data is in the attached spreadsheet.
EOF

# 4. Run Claude Code processing
python claude_runner_with_ai.py

# 5. Claude Code will:
#    - Read and understand the task
#    - Analyze what's needed
#    - Generate intelligent steps
#    - Create a detailed plan
#    - Determine routing

# 6. Check the plan
cat ai_employee_vault/Plans/plan-*.md
```

**Result:**
- Claude Code generates a detailed, context-aware plan
- Plan includes specific steps for data analysis
- Considers the complexity and creates appropriate workflow

---

## Hybrid Approach (Recommended)

Use both modes together:

1. **Automated Mode** for routine tasks:
   - File monitoring (scheduled)
   - Gmail checking (scheduled)
   - Simple task processing

2. **Claude Code Mode** for important tasks:
   - Complex analysis
   - Strategic planning
   - High-stakes communications

### Setup Hybrid Workflow

```bash
# 1. Setup Task Scheduler for automated mode
#    Runs every 15 minutes
#    Uses: python claude_runner.py

# 2. Manually process important tasks with Claude Code
#    When you see a complex task in Needs_Action/
#    Run: python claude_runner_with_ai.py (inside Claude Code CLI)
```

---

## Troubleshooting

### Issue: "Claude Code not found"

**Solution:**
```bash
# Install Claude Code CLI
# Follow instructions at: https://claude.ai/code

# Or use the web version
# Run the script and copy the prompt to Claude.ai
```

### Issue: "Task not processed by Claude Code"

**Solution:**
```bash
# Make sure you're running INSIDE Claude Code CLI
claude
cd silver-tier
python claude_runner_with_ai.py

# Claude Code should see the prompt and process it
```

### Issue: "Want to use Claude API directly"

**Solution:**
The current implementation shows the prompt for Claude Code.
To use Claude API directly, you would need to:
1. Add `anthropic` package
2. Create API client
3. Send prompt to Claude API
4. Parse response

This is intentionally not included to keep it hackathon-simple.

---

## Architecture Notes

### Automated Mode Architecture
```
claude_runner.py
    ↓
IntegratedRunner
    ↓
ReasoningSkill (pattern matching)
    ↓
ApprovalSkill (file-based)
    ↓
MCPServer (execution)
```

### Claude Code Mode Architecture
```
claude_runner_with_ai.py
    ↓
Generates prompt for Claude Code
    ↓
Claude Code CLI processes prompt
    ↓
Claude Code uses AI reasoning
    ↓
Claude Code generates plan
    ↓
Claude Code determines routing
```

---

## Best Practices

1. **Use Automated Mode for:**
   - Scheduled processing
   - High-volume tasks
   - Simple workflows

2. **Use Claude Code Mode for:**
   - Complex analysis
   - Strategic decisions
   - Important communications

3. **Monitor Both:**
   - Check activity.log for automated mode
   - Review plans generated by Claude Code mode

4. **Iterate:**
   - Start with automated mode
   - Switch to Claude Code mode for complex tasks
   - Refine patterns based on results

---

## Next Steps

1. Try both modes with test tasks
2. Compare the quality of plans generated
3. Decide which mode fits your workflow
4. Setup automation for routine tasks
5. Use Claude Code mode for important work

**Both modes are production-ready and can be used together!**
