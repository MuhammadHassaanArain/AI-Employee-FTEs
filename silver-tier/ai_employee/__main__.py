#!/usr/bin/env python3
"""AI Employee CLI Entry Point"""
import sys

def init_vault():
    from ai_employee.config import Config
    config = Config()
    vault_path = config.vault_path
    print(f"Initializing vault at: {vault_path}")
    folders = ["Inbox", "Needs_Action", "Plans", "Waiting_Approval", "Approved", "Rejected", "LinkedIn_Posts", "Done"]
    for folder in folders:
        (vault_path / folder).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {folder}/")
    print("\n✅ Vault initialized!")

def run_workflow():
    from ai_employee.runner import main
    return main()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_vault()
        return 0
    return run_workflow()

if __name__ == "__main__":
    sys.exit(main())
