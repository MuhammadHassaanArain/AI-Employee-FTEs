#!/usr/bin/env python3
"""
Test Reasoning Skill Integration with Claude Runner
"""

import sys
from pathlib import Path

def test_integration():
    """Test that claude_runner integrates with reasoning_skill."""
    print("INTEGRATION TEST: Claude Runner + Reasoning Skill")
    print("="*60)
    
    try:
        # Setup test vault
        from ai_employee.vault.manager import VaultManager
        from ai_employee.models.task import Task
        
        test_vault = Path("./test_vault_integration")
        vault_manager = VaultManager(str(test_vault))
        vault_manager.create_vault()
        
        # Create a test task in Needs_Action
        test_task = Task(
            title="Send quarterly report",
            content="Send an email to stakeholders@company.com with Q1 financial report. Include revenue growth and key metrics.",
            source="file",
        )
        
        needs_action = test_vault / "Needs_Action"
        task_file = needs_action / f"task-{test_task.id}.md"
        task_file.write_text(test_task.to_markdown(), encoding="utf-8")
        
        print(f"[OK] Created test task: {task_file.name}")
        
        # Import claude_runner
        from claude_runner import process_next_task
        
        print("[OK] Imported claude_runner.process_next_task")
        
        # Process the task
        print("\n[INFO] Processing task with claude_runner...")
        result = process_next_task(test_vault)
        
        print(f"[OK] Task processed: {result}")
        
        # Verify Plan.md was created
        plans_folder = test_vault / "Plans"
        plan_files = list(plans_folder.glob("plan-*.md"))
        
        if plan_files:
            print(f"[OK] Plan.md created: {plan_files[0].name}")
            
            # Read and display plan
            plan_content = plan_files[0].read_text(encoding="utf-8")
            print("\n[INFO] Plan preview:")
            print("-" * 60)
            lines = plan_content.split('\n')[:20]
            for line in lines:
                print(line)
            print("-" * 60)
        else:
            print("[FAIL] No Plan.md file created")
            return False
        
        # Check if task was routed correctly
        pending_approval = test_vault / "Pending_Approval"
        done_folder = test_vault / "Done"
        
        if list(pending_approval.glob("approval-*.md")):
            print("[OK] Task routed to Pending_Approval (needs approval)")
        elif list(done_folder.glob("task-*.md")):
            print("[OK] Task routed to Done (no approval needed)")
        else:
            print("[INFO] Task still in Needs_Action (expected for sensitive actions)")
        
        # Cleanup
        import shutil
        if test_vault.exists():
            shutil.rmtree(test_vault)
        
        print("\n[SUCCESS] Integration test passed!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration test."""
    result = test_integration()
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
