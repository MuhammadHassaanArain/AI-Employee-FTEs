"""
AI Employee - Silver Tier

Fully automated AI employee with:
- Two watchers (file + Gmail)
- Claude reasoning loop
- Human-in-the-loop approval
- Real LinkedIn API posting
- MCP server integration
- OS-level scheduling
"""

__version__ = "2.0.0"  # Silver Tier
__author__ = "Your Name"

from ai_employee.config import Config
from ai_employee.runner import AIEmployeeRunner

__all__ = ["Config", "AIEmployeeRunner"]
