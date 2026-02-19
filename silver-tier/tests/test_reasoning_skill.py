#!/usr/bin/env python3
"""
Test Reasoning Skill Implementation
"""

import sys
from pathlib import Path

def test_import():
    """Test that reasoning_skill can be imported."""
    print("TEST 1: Import Test")
    print("="*60)
    
    try:
        from ai_employee.skills.reasoning_skill import ReasoningSkill
        print("[OK] ReasoningSkill imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_instantiation():
    """Test that ReasoningSkill can be instantiated."""
    print("\nTEST 2: Instantiation Test")
    print("="*60)
    
    try:
        from ai_employee.skills.reasoning_skill import ReasoningSkill
        from ai_employee.vault.manager import VaultManager
        
        test_vault = Path("./test_vault_reasoning")
        
        # Create vault
        vault_manager = VaultManager(str(test_vault))
        vault_manager.create_vault()
        
        skill = ReasoningSkill(vault_path=test_vault)
        
        print("[OK] ReasoningSkill instantiated")
        print(f"[OK] Plans folder: {skill.plans_folder}")
        print(f"[OK] Action patterns: {len(skill.action_patterns)} types")
        
        # Cleanup
        import shutil
        if test_vault.exists():
            shutil.rmtree(test_vault)
        
        return True
    except Exception as e:
        print(f"[FAIL] Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_action_detection():
    """Test action type detection."""
    print("\nTEST 3: Action Detection Test")
    print("="*60)
    
    try:
        from ai_employee.skills.reasoning_skill import ReasoningSkill
        from ai_employee.vault.manager import VaultManager
        
        test_vault = Path("./test_vault_reasoning")
        vault_manager = VaultManager(str(test_vault))
        vault_manager.create_vault()
        
        skill = ReasoningSkill(vault_path=test_vault)
        
        test_cases = [
            ("Send email to client@example.com", "email"),
            ("Post to LinkedIn about our product", "linkedin"),
            ("Pay invoice for $500", "payment"),
            ("Research competitors in AI space", "research"),
            ("Schedule meeting for next week", "schedule"),
            ("Delete old files from server", "delete"),
        ]
        
        all_passed = True
        for content, expected_type in test_cases:
            detected = skill.detect_action_type(content)
            if detected == expected_type:
                print(f"[OK] '{content[:30]}...' -> {detected}")
            else:
                print(f"[FAIL] '{content[:30]}...' -> {detected} (expected {expected_type})")
                all_passed = False
        
        # Cleanup
        import shutil
        if test_vault.exists():
            shutil.rmtree(test_vault)
        
        return all_passed
    except Exception as e:
        print(f"[FAIL] Action detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plan_generation():
    """Test plan generation."""
    print("\nTEST 4: Plan Generation Test")
    print("="*60)
    
    try:
        from ai_employee.skills.reasoning_skill import ReasoningSkill
        from ai_employee.vault.manager import VaultManager
        from ai_employee.models.task import Task
        
        test_vault = Path("./test_vault_reasoning")
        vault_manager = VaultManager(str(test_vault))
        vault_manager.create_vault()
        
        skill = ReasoningSkill(vault_path=test_vault)
        
        # Create test task
        test_task = Task(
            title="Send project update email",
            content="Send an email to client@example.com with the Q1 project status update. Include timeline and budget.",
            source="file",
        )
        
        # Generate plan
        plan, needs_approval = skill.generate_plan(test_task)
        
        print(f"[OK] Plan generated for task: {test_task.title}")
        print(f"[OK] Steps: {len(plan.steps)}")
        print(f"[OK] Needs approval: {needs_approval}")
        print(f"[OK] Approval checkpoints: {len(plan.approval_checkpoints)}")
        print(f"[OK] Warnings: {len(plan.warnings)}")
        
        if plan.steps:
            print(f"\nFirst 3 steps:")
            for i, step in enumerate(plan.steps[:3], 1):
                print(f"  {i}. {step}")
        
        # Cleanup
        import shutil
        if test_vault.exists():
            shutil.rmtree(test_vault)
        
        return True
    except Exception as e:
        print(f"[FAIL] Plan generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("REASONING SKILL IMPLEMENTATION TEST")
    print("="*60)
    print()
    
    results = []
    results.append(("Import", test_import()))
    results.append(("Instantiation", test_instantiation()))
    results.append(("Action Detection", test_action_detection()))
    results.append(("Plan Generation", test_plan_generation()))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        print("\nReasoning Skill Features:")
        print("  - Dynamic action type detection (email, linkedin, payment, etc.)")
        print("  - Entity extraction (emails, URLs, amounts, dates)")
        print("  - Context-aware step generation")
        print("  - Intelligent approval detection")
        print("  - Handbook rule integration")
        print("  - Warning generation")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
