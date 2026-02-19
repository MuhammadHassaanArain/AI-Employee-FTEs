"""
CLI entry point for AI Employee (Bronze Tier - Claude Code Integration)
"""

import sys
import argparse
from ai_employee.config import Config
from ai_employee.vault.manager import VaultManager


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Personal AI Employee - Silver Tier (Functional Assistant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Obsidian vault")
    init_parser.add_argument(
        "--vault-path",
        default="./ai_employee_vault",
        help="Path to create vault (default: ./ai_employee_vault)",
    )

    # Watch command (replaces "run")
    watch_parser = subparsers.add_parser("watch", help="Watch for new files and create tasks")
    watch_parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
    )
    watch_parser.add_argument(
        "--watch-folder",
        help="Folder to monitor for new files",
    )
    watch_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Display current configuration",
    )

    # Scheduler command (Silver Tier)
    scheduler_parser = subparsers.add_parser("scheduler", help="Run Silver Tier scheduler (automated mode)")
    scheduler_parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
    )
    scheduler_parser.add_argument(
        "--no-initial",
        action="store_true",
        help="Skip initial cycle on startup",
    )
    scheduler_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "init":
            # Initialize vault
            from ai_employee.vault.manager import VaultManager
            vault_manager = VaultManager(args.vault_path)
            vault_manager.create_vault()
            print(f"[OK] Vault initialized at: {args.vault_path}")
            print(f"[OK] Open in Obsidian: {args.vault_path}")
            print(f"\nNext steps:")
            print(f"  1. Run: python -m ai_employee watch")
            print(f"  2. Drop files in: {args.vault_path}/Inbox")
            print(f"  3. Process tasks: python claude_runner.py")

        elif args.command == "watch":
            # Load configuration
            config = Config(
                vault_path=args.vault_path,
                watch_folder=args.watch_folder,
                log_level=args.log_level,
            )

            # Setup logging
            from ai_employee.utils.logger import setup_logger
            setup_logger(
                "ai_employee",
                log_file=config.vault_path / "activity.log",
                level=config.log_level,
            )

            # Validate vault structure
            from ai_employee.vault.manager import VaultManager
            vault_manager = VaultManager(str(config.vault_path))
            if not vault_manager.validate_structure():
                print("ERROR: Vault structure is invalid. Run 'init' first.")
                sys.exit(1)

            print(f"AI Employee - File Watcher (Bronze Tier)")
            print(f"Vault: {config.vault_path}")
            print(f"Watching: {config.watch_folder}")
            print(f"Press Ctrl+C to stop\n")

            # Start file watcher
            from ai_employee.watchers.file_watcher import FileWatcher

            watcher = FileWatcher(
                watch_folder=config.watch_folder,
                vault_path=config.vault_path,
            )

            try:
                watcher.start()
                print(f"[OK] File watcher started")
                print(f"[OK] Monitoring: {config.watch_folder}")
                print(f"[OK] Dashboard: {config.vault_path / 'Dashboard.md'}")
                print(f"\nWatcher is running. New files will be captured as tasks.")
                print(f"To process tasks, run: python claude_runner.py\n")

                # Keep running
                import time
                while watcher.is_alive():
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n\nShutting down gracefully...")
                watcher.stop()
                print("[OK] File watcher stopped")
                sys.exit(0)

        elif args.command == "config":
            # Show configuration
            config = Config()
            print("Current Configuration:")
            print(f"  Vault Path: {config.vault_path}")
            print(f"  Watch Folder: {config.watch_folder}")
            print(f"  Log Level: {config.log_level}")
            print(f"  Mode: Silver Tier (Functional Assistant)")

        elif args.command == "scheduler":
            # Run Silver Tier scheduler
            config = Config(
                vault_path=args.vault_path,
                log_level=args.log_level,
            )

            # Setup logging
            from ai_employee.utils.logger import setup_logger
            setup_logger(
                "ai_employee",
                log_file=config.vault_path / "activity.log",
                level=config.log_level,
            )

            # Validate vault structure
            from ai_employee.vault.manager import VaultManager
            vault_manager = VaultManager(str(config.vault_path))
            if not vault_manager.validate_structure():
                print("ERROR: Vault structure is invalid. Run 'init' first.")
                sys.exit(1)

            print(f"AI Employee - Silver Tier Scheduler")
            print(f"Vault: {config.vault_path}")
            print(f"Press Ctrl+C to stop\n")

            # Start scheduler
            from ai_employee.scheduler import Scheduler

            scheduler = Scheduler(config)
            scheduler.start(run_initial=not args.no_initial)

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
