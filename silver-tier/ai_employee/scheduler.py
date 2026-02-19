"""
Scheduler (Silver Tier)

Automation scheduler for running watchers, reasoning loop, and approval workflow.
Uses simple scheduling to run components at regular intervals.

Silver Tier Requirement: Basic scheduling (cron or Task Scheduler).
"""

import time
import schedule
from pathlib import Path
from datetime import datetime
from ai_employee.config import Config
from ai_employee.watchers.file_watcher import FileWatcher
from ai_employee.watchers.gmail_watcher import GmailWatcher
from ai_employee.skills.approval_skill import ApprovalSkill
from ai_employee.skills.linkedin_skill import LinkedInSkill
from ai_employee.utils.logger import get_logger, setup_logger

logger = get_logger(__name__)


class Scheduler:
    """
    Silver Tier Scheduler.

    Runs components at regular intervals:
    - Gmail watcher: Every 5 minutes
    - File watcher: Continuous (already running)
    - Claude runner: Every 5 minutes (processes tasks)
    - Approval workflow: Every 5 minutes
    - LinkedIn poster: Every 1 hour
    """

    def __init__(self, config: Config):
        """
        Initialize scheduler.

        Args:
            config: Configuration object
        """
        self.config = config
        self.vault_path = config.vault_path

        # Initialize components
        self.gmail_watcher = GmailWatcher(vault_path=self.vault_path)
        self.approval_skill = ApprovalSkill(vault_path=self.vault_path)
        self.linkedin_skill = LinkedInSkill(vault_path=self.vault_path)

        logger.info("Scheduler initialized (Silver Tier)")

    def run_gmail_watcher(self):
        """
        Run Gmail watcher cycle.

        TODO:
        - Call gmail_watcher.run_once()
        - Log results
        - Handle errors
        """
        try:
            logger.info("Running Gmail watcher...")
            tasks_created = self.gmail_watcher.run_once()
            logger.info(f"Gmail watcher completed. Tasks created: {tasks_created}")
        except Exception as e:
            logger.error(f"Error in Gmail watcher: {e}")

    def run_claude_runner(self):
        """
        Run Claude runner to process tasks.

        TODO:
        - Import and call claude_runner logic
        - Process tasks from Needs_Action/
        - Generate plans
        - Route to approval or done
        - Log results
        """
        try:
            logger.info("Running Claude runner...")
            # TODO: Import and call claude_runner
            # For now, just log
            logger.info("Claude runner completed (placeholder)")
        except Exception as e:
            logger.error(f"Error in Claude runner: {e}")

    def run_approval_workflow(self):
        """
        Run approval workflow to process pending approvals.

        TODO:
        - Call approval_skill.process_pending_approvals()
        - Execute approved actions via MCP
        - Log results
        """
        try:
            logger.info("Running approval workflow...")
            results = self.approval_skill.process_pending_approvals()
            logger.info(f"Approval workflow completed: {results}")
        except Exception as e:
            logger.error(f"Error in approval workflow: {e}")

    def run_linkedin_poster(self):
        """
        Run LinkedIn poster to publish queued posts.

        TODO:
        - Call linkedin_skill.process_queue()
        - Post to LinkedIn
        - Log results
        """
        try:
            logger.info("Running LinkedIn poster...")
            results = self.linkedin_skill.process_queue()
            logger.info(f"LinkedIn poster completed: {results}")
        except Exception as e:
            logger.error(f"Error in LinkedIn poster: {e}")

    def setup_schedule(self):
        """
        Set up scheduled jobs.

        Schedule:
        - Gmail watcher: Every 5 minutes
        - Claude runner: Every 5 minutes
        - Approval workflow: Every 5 minutes
        - LinkedIn poster: Every 1 hour
        """
        logger.info("Setting up schedule...")

        # Gmail watcher: Every 5 minutes
        schedule.every(5).minutes.do(self.run_gmail_watcher)

        # Claude runner: Every 5 minutes
        schedule.every(5).minutes.do(self.run_claude_runner)

        # Approval workflow: Every 5 minutes
        schedule.every(5).minutes.do(self.run_approval_workflow)

        # LinkedIn poster: Every 1 hour
        schedule.every(1).hours.do(self.run_linkedin_poster)

        logger.info("Schedule configured:")
        logger.info("  - Gmail watcher: Every 5 minutes")
        logger.info("  - Claude runner: Every 5 minutes")
        logger.info("  - Approval workflow: Every 5 minutes")
        logger.info("  - LinkedIn poster: Every 1 hour")

    def run_initial_cycle(self):
        """
        Run all jobs once immediately on startup.
        """
        logger.info("Running initial cycle...")

        self.run_gmail_watcher()
        self.run_claude_runner()
        self.run_approval_workflow()
        self.run_linkedin_poster()

        logger.info("Initial cycle completed")

    def start(self, run_initial: bool = True):
        """
        Start scheduler.

        Args:
            run_initial: Run all jobs once immediately (default: True)

        TODO:
        - Set up schedule
        - Run initial cycle if requested
        - Enter main loop
        - Handle keyboard interrupt
        """
        logger.info("Starting Silver Tier Scheduler...")

        # Set up schedule
        self.setup_schedule()

        # Run initial cycle
        if run_initial:
            self.run_initial_cycle()

        # Main loop
        logger.info("Scheduler running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop()

    def stop(self):
        """
        Stop scheduler and clean up.
        """
        logger.info("Stopping scheduler...")
        schedule.clear()
        logger.info("Scheduler stopped")


def main():
    """CLI entry point for scheduler."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Silver Tier Scheduler - Automated AI Employee"
    )
    parser.add_argument(
        "--no-initial",
        action="store_true",
        help="Skip initial cycle on startup",
    )
    parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Load configuration
    config = Config(
        vault_path=args.vault_path,
        log_level=args.log_level,
    )

    # Setup logging
    setup_logger(
        "ai_employee",
        log_file=config.vault_path / "activity.log",
        level=config.log_level,
    )

    # Create and start scheduler
    scheduler = Scheduler(config)

    try:
        scheduler.start(run_initial=not args.no_initial)
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
