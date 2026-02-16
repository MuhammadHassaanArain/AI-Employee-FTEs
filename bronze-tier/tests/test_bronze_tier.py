#!/usr/bin/env python
"""
Quick integration test for Bronze Tier implementation.
Tests vault initialization and basic structure.
"""

import sys
from pathlib import Path
import shutil

def test_vault_initialization():
    """Test vault initialization creates correct structure"""
    print("Testing Bronze Tier Implementation...")
    print("=" * 60)

    # Import after adding to path
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_employee.vault.manager import VaultManager

    # Test vault path
    test_vault = Path("./test_vault_temp")

    # Clean up if exists
    if test_vault.exists():
        shutil.rmtree(test_vault)

    print("\n1. Testing Vault Initialization...")
    vault_manager = VaultManager(str(test_vault))
    vault_manager.create_vault()

    # Verify structure
    checks = {
        "Vault root": test_vault.exists(),
        "Inbox folder": (test_vault / "Inbox").exists(),
        "Needs_Action folder": (test_vault / "Needs_Action").exists(),
        "Done folder": (test_vault / "Done").exists(),
        "Dashboard.md": (test_vault / "Dashboard.md").exists(),
        "Company_Handbook.md": (test_vault / "Company_Handbook.md").exists(),
    }

    # Check that Plans folder does NOT exist
    checks["Plans folder NOT created"] = not (test_vault / "Plans").exists()

    all_passed = True
    for check_name, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    # Verify Dashboard format
    print("\n2. Testing Dashboard Format...")
    dashboard_content = (test_vault / "Dashboard.md").read_text()

    dashboard_checks = {
        "Has title": "# AI Employee Dashboard" in dashboard_content,
        "Has Task Counts section": "## Task Counts" in dashboard_content,
        "Has Inbox count": "- Inbox:" in dashboard_content,
        "Has Needs_Action count": "- Needs_Action:" in dashboard_content,
        "Has Done count": "- Done:" in dashboard_content,
        "Has Activity Log section": "## Activity Log" in dashboard_content,
        "Simple format (no complex fields)": "System Status" not in dashboard_content,
    }

    for check_name, result in dashboard_checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    # Verify Handbook format
    print("\n3. Testing Handbook Format...")
    handbook_content = (test_vault / "Company_Handbook.md").read_text()

    handbook_checks = {
        "Has title": "# Company Handbook" in handbook_content,
        "Has Rules section": "## Rules" in handbook_content,
        "Simple format": "[CRITICAL]" in handbook_content or "[HIGH]" in handbook_content,
        "No complex structure": "**Keywords**:" not in handbook_content,
    }

    for check_name, result in handbook_checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    # Clean up
    print("\n4. Cleaning up test vault...")
    shutil.rmtree(test_vault)
    print("  [PASS] Test vault removed")

    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Bronze Tier structure is correct!")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED - Review output above")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_vault_initialization()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
