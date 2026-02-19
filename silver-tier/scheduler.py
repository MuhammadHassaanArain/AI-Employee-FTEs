#!/usr/bin/env python3
"""
Scheduler for AI Employee (Silver Tier)

Runs the integrated workflow periodically.

Usage:
    # Run continuously (every 15 minutes)
    python scheduler.py

    # Run once and exit (for Windows Task Scheduler)
    python scheduler.py --once

    # Custom interval (every 30 minutes)
    python scheduler.py --interval 30
"""

import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from ai_employee.config import Config
from claude_runner import IntegratedRunner
from ai_employee.utils.logger import get_logger

logger = get_logger(__name__)


def run_workflow(config: Config):
    """
    Run the integrated workflow once.

    Args:
        config: Configuration object
    """
    print("\n" + "=" * 80)
    print(f"SCHEDULER RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        runner = IntegratedRunner(config)
        runner.run()
        logger.info("Workflow completed successfully")
        return True
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        print(f"\nERROR: {e}")
        return False


def run_continuous(config: Config, interval_minutes: int):
    """
    Run workflow continuously at specified interval.

    Args:
        config: Configuration object
        interval_minutes: Interval between runs in minutes
    """
    import schedule

    print("\n" + "=" * 80)
    print("AI EMPLOYEE SCHEDULER - CONTINUOUS MODE")
    print("=" * 80)
    print(f"Interval: Every {interval_minutes} minutes")
    print(f"Vault: {config.vault_path}")
    print("Press Ctrl+C to stop")
    print("=" * 80 + "\n")

    # Schedule the job
    schedule.every(interval_minutes).minutes.do(run_workflow, config)

    # Run immediately on start
    print("Running initial workflow...")
    run_workflow(config)

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        logger.info("Scheduler stopped by user")


def run_once(config: Config):
    """
    Run workflow once and exit (for Windows Task Scheduler).

    Args:
        config: Configuration object
    """
    print("\n" + "=" * 80)
    print("AI EMPLOYEE SCHEDULER - SINGLE RUN MODE")
    print("=" * 80)
    print(f"Vault: {config.vault_path}")
    print("=" * 80 + "\n")

    success = run_workflow(config)
    return 0 if success else 1


def main():
    """Main entry point for scheduler"""
    parser = argparse.ArgumentParser(
        description="AI Employee Scheduler - Run workflow periodically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run continuously every 15 minutes (default)
  python scheduler.py

  # Run continuously every 30 minutes
  python scheduler.py --interval 30

  # Run once and exit (for Windows Task Scheduler)
  python scheduler.py --once

Windows Task Scheduler Setup:
  1. Open Task Scheduler
  2. Create Basic Task
  3. Set trigger (e.g., every 15 minutes)
  4. Action: Start a program
  5. Program: python.exe
  6. Arguments: scheduler.py --once
  7. Start in: <path-to-silver-tier-folder>
        """,
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for Windows Task Scheduler)",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Interval between runs in minutes (default: 15)",
    )

    parser.add_argument(
        "--vault-path",
        type=str,
        help="Path to Obsidian vault (default: ./ai_employee_vault)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = Config(vault_path=args.vault_path)

        # Validate vault
        if not config.vault_path.exists():
            print(f"ERROR: Vault not found at {config.vault_path}")
            print("Run: python -m ai_employee init")
            return 1

        # Run based on mode
        if args.once:
            return run_once(config)
        else:
            run_continuous(config, args.interval)
            return 0

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
