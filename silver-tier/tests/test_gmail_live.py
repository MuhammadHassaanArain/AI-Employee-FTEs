#!/usr/bin/env python3
"""
Live Gmail Watcher Test

This script tests the Gmail watcher with real credentials.
Make sure to set GMAIL_EMAIL and GMAIL_PASSWORD in .env first.
"""

import sys
import os
from pathlib import Path

def main():
    print("LIVE GMAIL WATCHER TEST")
    print("="*60)
    
    # Check credentials
    email = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_PASSWORD")
    
    if not email or not password:
        print("[ERROR] Gmail credentials not configured")
        print("\nSet environment variables:")
        print("  GMAIL_EMAIL=your-email@gmail.com")
        print("  GMAIL_PASSWORD=your-app-password")
        print("\nOr add to .env file:")
        print("  GMAIL_EMAIL=your-email@gmail.com")
        print("  GMAIL_PASSWORD=your-app-password")
        return 1
    
    print(f"[OK] Email configured: {email}")
    print(f"[OK] Password configured: {'*' * len(password)}")
    print()
    
    # Initialize vault
    from ai_employee.vault.manager import VaultManager
    
    vault_path = Path("./ai_employee_vault")
    if not vault_path.exists():
        print("[INFO] Initializing vault...")
        vault_manager = VaultManager(str(vault_path))
        vault_manager.create_vault()
        print(f"[OK] Vault created at: {vault_path}")
    else:
        print(f"[OK] Using existing vault: {vault_path}")
    
    print()
    
    # Test Gmail watcher
    from ai_employee.watchers.gmail_watcher import GmailWatcher
    
    print("[INFO] Initializing Gmail watcher...")
    watcher = GmailWatcher(vault_path=vault_path)
    
    print("[INFO] Connecting to Gmail...")
    print("[INFO] Checking for unread emails...")
    print()
    
    try:
        tasks_created = watcher.check_gmail()
        
        print()
        print("="*60)
        print("RESULTS")
        print("="*60)
        print(f"Tasks created: {tasks_created}")
        
        if tasks_created > 0:
            print(f"\n[SUCCESS] Created {tasks_created} task(s) from emails")
            print(f"Check: {vault_path}/Needs_Action/")
        else:
            print("\n[INFO] No unread emails found")
            print("Send yourself a test email and run again")
        
        return 0
        
    except Exception as e:
        print()
        print("="*60)
        print("ERROR")
        print("="*60)
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
