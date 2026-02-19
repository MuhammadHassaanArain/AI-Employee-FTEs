"""
Personal AI Employee - Silver Tier

Functional Assistant with multi-source watchers, reasoning loop,
approval workflow, MCP server, and automated scheduling.
"""

from setuptools import setup, find_packages

setup(
    name="ai-employee-silver",
    version="2.0.0",
    description="Personal AI Employee - Silver Tier (Functional Assistant)",
    author="Muhammad Hassaan",
    author_email="hassaanarain008@gmail.com",
    packages=find_packages(),
    install_requires=[
        # Bronze Tier dependencies
        "anthropic>=0.18.0",
        "watchdog>=4.0.0",
        "python-frontmatter>=1.0.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.0",
        "pyyaml>=6.0.0",
        # Silver Tier dependencies
        "schedule>=1.2.0",  # Scheduler
        "google-api-python-client>=2.0.0",  # Gmail API
        "google-auth>=2.0.0",  # Gmail OAuth
        "google-auth-oauthlib>=1.0.0",  # Gmail OAuth flow
        "google-auth-httplib2>=0.1.0",  # Gmail HTTP
        "requests>=2.31.0",  # LinkedIn API (custom implementation)
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-mock>=3.12.0",
            "black>=24.0.0",
            "pylint>=3.0.0",
            "flake8>=7.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-employee=ai_employee.__main__:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
