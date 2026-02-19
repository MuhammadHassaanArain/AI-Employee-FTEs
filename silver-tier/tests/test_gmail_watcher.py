#!/usr/bin/env python3
"""
Test Gmail Watcher Implementation
"""

import sys
from pathlib import Path

def test_import():
    """Test that gmail_watcher can be imported."""
    print("TEST 1: Import Test")
    print("="*60)
    
    try:
        from ai_employee.watchers.gmail_watcher import GmailWatcher
        print("[OK] GmailWatcher imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_instantiation():
    """Test that GmailWatcher can be instantiated."""
    print("\nTEST 2: Instantiation Test")
    print("="*60)
    
    try:
        from ai_employee.watchers.gmail_watcher import GmailWatcher
        
        test_vault = Path("./test_vault_gmail")
        test_vault.mkdir(exist_ok=True)
        
        watcher = GmailWatcher(
            vault_path=test_vault,
            email_address="test@example.com",
            password="test-password"
        )
        
        print("[OK] GmailWatcher instantiated")
        print(f"[OK] Email: {watcher.email_address}")
        print(f"[OK] IMAP Server: {watcher.imap_server}")
        
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

def test_methods():
    """Test that all required methods exist."""
    print("\nTEST 3: Method Existence Test")
    print("="*60)
    
    try:
        from ai_employee.watchers.gmail_watcher import GmailWatcher
        
        required_methods = [
            'connect',
            'fetch_unread_emails',
            'create_task_from_email',
            'mark_as_read',
            'check_gmail',
            'run_once',
        ]
        
        all_exist = True
        for method_name in required_methods:
            if hasattr(GmailWatcher, method_name):
                print(f"[OK] Method exists: {method_name}()")
            else:
                print(f"[FAIL] Method missing: {method_name}()")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"[FAIL] Method test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("GMAIL WATCHER IMPLEMENTATION TEST")
    print("="*60)
    print()
    
    results = []
    results.append(("Import", test_import()))
    results.append(("Instantiation", test_instantiation()))
    results.append(("Methods", test_methods()))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("1. Set GMAIL_EMAIL and GMAIL_PASSWORD in .env")
        print("2. Run: python -m ai_employee.watchers.gmail_watcher")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
