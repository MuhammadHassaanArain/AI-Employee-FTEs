#!/usr/bin/env python
"""
Demo script to showcase the beautiful rich logging output

Run this to see the enhanced logging in action:
    python demo_logging.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_employee.utils.logger import setup_logger, get_logger

# Setup logger with rich formatting
logger = setup_logger("demo", level="DEBUG")

def demo_logging():
    """Demonstrate all logging levels with rich formatting"""

    print("\n" + "="*60)
    print("  Bronze Tier AI Employee - Rich Logging Demo")
    print("="*60 + "\n")

    time.sleep(0.5)

    # DEBUG - Dim gray
    logger.debug("Initializing vault structure")
    time.sleep(0.3)

    # INFO - Cyan
    logger.info("Starting file watcher on vault/Inbox")
    time.sleep(0.3)

    logger.info("Monitoring for new files...")
    time.sleep(0.3)

    # SUCCESS - Green (custom level)
    logger.success("File detected: sales_report.txt")
    time.sleep(0.3)

    logger.info("Creating task from file")
    time.sleep(0.3)

    logger.success("Task created: task-abc123")
    time.sleep(0.3)

    logger.info("Generating AI plan with Claude")
    time.sleep(0.5)

    logger.success("Plan generated with 6 steps in 2.3s")
    time.sleep(0.3)

    logger.success("Task moved to Done folder")
    time.sleep(0.3)

    # WARNING - Yellow
    logger.warning("API rate limit approaching (80% used)")
    time.sleep(0.3)

    # ERROR - Red
    logger.error("Failed to process task-xyz789: Invalid file format")
    time.sleep(0.3)

    # More INFO
    logger.info("Dashboard updated: 3 tasks completed")
    time.sleep(0.3)

    logger.success("Processing cycle complete")

    print("\n" + "="*60)
    print("  Demo Complete - Notice the beautiful colors!")
    print("="*60 + "\n")

    # Demonstrate exception handling with rich traceback
    print("\nDemonstrating rich traceback (intentional error):\n")
    time.sleep(1)

    try:
        # Intentional error to show rich traceback
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Caught exception: {e}", exc_info=True)

    print("\n" + "="*60)
    print("  Notice the beautiful traceback with syntax highlighting!")
    print("="*60 + "\n")


def demo_deduplication():
    """Demonstrate error deduplication"""

    print("\n" + "="*60)
    print("  Demonstrating Error Deduplication")
    print("="*60 + "\n")

    logger.info("Simulating repeated errors (should only show once)...")
    time.sleep(0.5)

    # These will be deduplicated - only first one shows
    for i in range(5):
        logger.error("Authentication failed: Invalid API key")
        time.sleep(0.1)

    time.sleep(0.5)
    logger.info("Notice: Only 1 error shown instead of 5 (deduplication working!)")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    demo_logging()
    time.sleep(1)
    demo_deduplication()
