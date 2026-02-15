"""
CLI entry point for AI Employee
"""

import sys
import argparse
from ai_employee.config import Config
from ai_employee.vault.manager import VaultManager


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Personal AI Employee - Bronze Tier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Obsidian vault")
    init_parser.add_argument(
        "--vault-path",
        default="./AI_Employee_Vault",
        help="Path to create vault (default: ./AI_Employee_Vault)",
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the AI Employee")
    run_parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
    )
    run_parser.add_argument(
        "--watch-folder",
        help="Folder to monitor for new files",
    )
    run_parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum tasks to process per cycle",
    )
    run_parser.add_argument(
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "init":
            # Initialize vault
            vault_manager = VaultManager(args.vault_path)
            vault_manager.create_vault()
            print(f"✓ Vault initialized at: {args.vault_path}")
            print(f"✓ Open in Obsidian: {args.vault_path}")

        elif args.command == "run":
            # Load configuration
            config = Config(
                vault_path=args.vault_path,
                watch_folder=args.watch_folder,
                max_iterations=args.max_iterations,
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

            print(f"Starting AI Employee...")
            print(f"Vault: {config.vault_path}")
            print(f"Watching: {config.watch_folder}")
            print(f"Max iterations: {config.max_iterations}")
            print(f"Press Ctrl+C to stop\n")

            # Start file watcher
            from ai_employee.watcher.file_watcher import FileWatcher
            from ai_employee.processor.task_processor import TaskProcessor

            watcher = FileWatcher(
                watch_folder=config.watch_folder,
                vault_path=config.vault_path,
            )

            processor = TaskProcessor(
                vault_path=config.vault_path,
                api_key=config.anthropic_api_key,
                max_iterations=config.max_iterations,
            )

            try:
                watcher.start()
                print(f"✓ File watcher started")
                print(f"✓ Monitoring: {config.watch_folder}")
                print(f"✓ Dashboard: {config.vault_path / 'Dashboard.md'}")
                print(f"✓ Processing tasks automatically\n")

                # Keep running and process tasks periodically
                import time
                while watcher.is_alive():
                    # Process any pending tasks
                    try:
                        processor.process_tasks()
                    except Exception as e:
                        logger.error(f"Error processing tasks: {e}")

                    # Wait before next cycle
                    time.sleep(10)

            except KeyboardInterrupt:
                print("\n\nShutting down gracefully...")
                watcher.stop()
                print("✓ File watcher stopped")
                print("✓ All tasks saved")
                sys.exit(0)

        elif args.command == "config":
            # Show configuration
            config = Config()
            print("Current Configuration:")
            print(f"  Vault Path: {config.vault_path}")
            print(f"  Watch Folder: {config.watch_folder}")
            print(f"  Max Iterations: {config.max_iterations}")
            print(f"  Log Level: {config.log_level}")
            print(f"  API Key: {'Set' if config.anthropic_api_key else 'Not Set'}")

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
