# Bronze Tier - Quick Start Guide

## 5-Minute Setup

### Step 1: Install (1 min)
```bash
cd bronze-tier
pip install -e .
```

### Step 2: Configure API Key (1 min)
```bash
# Copy template
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 3: Initialize Vault (30 sec)
```bash
python -m ai_employee init
```

**Expected Output:**
```
✓ Vault initialized at: ./ai_employee_vault
✓ Open in Obsidian: ./ai_employee_vault
```

### Step 4: Run System (30 sec)
```bash
python -m ai_employee run
```

**Expected Output:**
```
Starting AI Employee...
Vault: ai_employee_vault
Watching: ai_employee_vault\Inbox
Max iterations: 10
Press Ctrl+C to stop

✓ File watcher started
✓ Monitoring: ai_employee_vault\Inbox
✓ Dashboard: ai_employee_vault\Dashboard.md
✓ Processing tasks automatically
```

### Step 5: Test It (2 min)

**Open a NEW terminal** (keep the system running) and run:

```bash
cd bronze-tier

# Test 1: Simple task
echo "Review the Q1 sales report and prepare a summary for the team meeting" > ai_employee_vault/Inbox/sales_task.txt

# Wait 10-15 seconds, then check results
```

**Verify Results:**

1. **Check Done folder:**
   ```bash
   ls ai_employee_vault/Done/
   # Should show: task-[uuid].md
   ```

2. **View the task with AI plan:**
   ```bash
   # Open the task file (replace [uuid] with actual ID)
   cat ai_employee_vault/Done/task-*.md
   ```

   **Expected content:**
   ```markdown
   ---
   id: [uuid]
   title: Review the Q1 sales report...
   status: done
   ---

   Review the Q1 sales report and prepare a summary for the team meeting

   ---

   ## AI Generated Plan

   1. Locate the Q1 sales report document
   2. Review key metrics and performance indicators
   3. Identify trends and notable changes
   4. Prepare a concise summary (under 200 words)
   5. Format summary with bullet points
   6. Share with team before meeting
   ```

3. **Check Dashboard:**
   ```bash
   cat ai_employee_vault/Dashboard.md
   ```

   **Expected content:**
   ```markdown
   # AI Employee Dashboard

   ## Task Counts
   - Inbox: 1
   - Needs_Action: 0
   - Done: 1

   ## Activity Log

   [timestamp] | file_detected | Detected new file: sales_task.txt | success
   [timestamp] | task_created | Created task: Review the Q1... | success
   [timestamp] | plan_generated | Generated plan with 6 steps | success
   [timestamp] | task_moved | Moved task to Done | success
   ```

4. **Verify original file preserved:**
   ```bash
   ls ai_employee_vault/Inbox/
   # Should still show: sales_task.txt (NOT deleted)
   ```

## Test Multiple Files

```bash
# Add 3 more tasks
echo "Send invoice to client ABC for project XYZ" > ai_employee_vault/Inbox/invoice.txt
echo "Schedule team meeting for next week" > ai_employee_vault/Inbox/meeting.txt
echo "Update documentation for new API endpoints" > ai_employee_vault/Inbox/docs.txt

# Wait 30 seconds
# All 3 should be processed and moved to Done/
```

## View in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `bronze-tier/ai_employee_vault`
4. Browse:
   - `Dashboard.md` - See task counts
   - `Done/` folder - View completed tasks with AI plans
   - `Company_Handbook.md` - View/edit behavior rules

## Stop the System

Press `Ctrl+C` in the terminal running the AI Employee:

```
^C

Shutting down gracefully...
✓ File watcher stopped
✓ All tasks saved
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check `.env` file exists in `bronze-tier/` directory
- Verify it contains: `ANTHROPIC_API_KEY=sk-ant-...`
- No quotes needed around the key

### "No module named 'ai_employee'"
- Run: `pip install -e .` from `bronze-tier/` directory
- Activate virtual environment if using one

### Files not being detected
- Verify files are in `ai_employee_vault/Inbox/`
- Check console output for errors
- View logs: `tail -f ai_employee_vault/activity.log`

### Plans not generated
- Check API key is valid
- Verify internet connection
- Look for errors in console output
- Check rate limits: `grep "rate limit" ai_employee_vault/activity.log`

## Success Criteria

✓ Files detected within 60 seconds
✓ Tasks created with YAML metadata
✓ AI plans generated and appended
✓ Tasks moved to Done folder
✓ Original files preserved in Inbox
✓ Dashboard shows accurate counts
✓ Activity log records all actions

## What's Working

- ✓ File monitoring (Inbox folder)
- ✓ Task creation (markdown with YAML)
- ✓ AI plan generation (Claude API)
- ✓ Handbook rule application
- ✓ Task completion (move to Done)
- ✓ Dashboard updates
- ✓ Activity logging
- ✓ Error handling
- ✓ Graceful shutdown

## Next Steps

1. **Customize Handbook**: Edit `ai_employee_vault/Company_Handbook.md`
2. **Add More Tasks**: Drop files in `Inbox/`
3. **Monitor Dashboard**: Watch counts update in real-time
4. **Review Plans**: Check AI-generated plans in `Done/` folder
5. **Iterate**: Refine handbook rules based on results

## Performance Expectations

- File detection: < 60 seconds
- Plan generation: < 10 seconds per task
- 10 tasks processed: < 5 minutes
- System uptime: 24+ hours without crashes

## Ready for Hackathon Demo ✓

The Bronze Tier implementation is complete and tested.
