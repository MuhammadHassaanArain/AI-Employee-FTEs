#!/usr/bin/env python3
"""
Silver Tier Structure Verification Script

Tests that all modules can be imported and basic structure is correct.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all Silver Tier modules can be imported."""
    print("Testing Silver Tier imports...")
    
    try:
        # Core modules
        from ai_employee import config
        print("[OK] ai_employee.config")
        
        # Watchers
        from ai_employee.watchers import FileWatcher, GmailWatcher, TaskCreator
        print("[OK] ai_employee.watchers (FileWatcher, GmailWatcher, TaskCreator)")
        
        # Skills
        from ai_employee.skills import ReasoningSkill, ApprovalSkill, EmailSkill, LinkedInSkill
        print("[OK] ai_employee.skills (ReasoningSkill, ApprovalSkill, EmailSkill, LinkedInSkill)")
        
        # MCP
        from ai_employee.mcp import MCPServer
        print("[OK] ai_employee.mcp (MCPServer)")
        
        # Scheduler
        from ai_employee.scheduler import Scheduler
        print("[OK] ai_employee.scheduler (Scheduler)")
        
        # Models
        from ai_employee.models.task import Task
        from ai_employee.models.plan import Plan
        print("[OK] ai_employee.models (Task, Plan)")
        
        # Vault
        from ai_employee.vault.manager import VaultManager
        print("[OK] ai_employee.vault (VaultManager)")
        
        print("\n[SUCCESS] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n[FAIL] Import failed: {e}")
        return False

def test_vault_structure():
    """Test vault initialization with Silver Tier folders."""
    print("\nTesting vault structure...")
    
    try:
        from ai_employee.vault.manager import VaultManager
        
        test_vault = Path("./test_vault_silver")
        
        # Clean up if exists
        if test_vault.exists():
            import shutil
            shutil.rmtree(test_vault)
        
        # Create vault
        vault_manager = VaultManager(str(test_vault))
        vault_manager.create_vault()
        
        # Check folders
        expected_folders = [
            "Inbox",
            "Needs_Action",
            "Done",
            "Plans",
            "Pending_Approval",
            "Approved",
            "Rejected",
            "LinkedIn_Queue",
        ]
        
        all_ok = True
        for folder in expected_folders:
            folder_path = test_vault / folder
            if folder_path.exists():
                print(f"[OK] {folder}/")
            else:
                print(f"[FAIL] {folder}/ (missing)")
                all_ok = False
        
        # Check files
        expected_files = [
            "Dashboard.md",
            "Company_Handbook.md",
            "activity.log",
        ]
        
        for file in expected_files:
            file_path = test_vault / file
            if file_path.exists():
                print(f"[OK] {file}")
            else:
                print(f"[FAIL] {file} (missing)")
                all_ok = False
        
        # Clean up
        import shutil
        shutil.rmtree(test_vault)
        
        if all_ok:
            print("\n[SUCCESS] Vault structure correct!")
        return all_ok
        
    except Exception as e:
        print(f"\n[FAIL] Vault test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_model():
    """Test Task model with Silver Tier fields."""
    print("\nTesting Task model...")
    
    try:
        from ai_employee.models.task import Task
        
        # Create task with Silver Tier fields
        task = Task(
            title="Test Task",
            content="Test content",
            source="gmail",
            source_metadata={"email_id": "12345", "from": "test@example.com"},
        )
        
        # Check fields
        assert task.source == "gmail", "Source field not set"
        assert task.source_metadata["email_id"] == "12345", "Source metadata not set"
        
        # Test serialization
        task_dict = task.to_dict()
        assert "source" in task_dict, "Source not in dict"
        assert "source_metadata" in task_dict, "Source metadata not in dict"
        
        print("[OK] Task model has source field")
        print("[OK] Task model has source_metadata field")
        print("[OK] Task serialization works")
        
        print("\n[SUCCESS] Task model correct!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Task model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests."""
    print("="*60)
    print("SILVER TIER STRUCTURE VERIFICATION")
    print("="*60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test vault structure
    results.append(("Vault Structure", test_vault_structure()))
    
    # Test task model
    results.append(("Task Model", test_task_model()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! Silver Tier structure is ready.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
