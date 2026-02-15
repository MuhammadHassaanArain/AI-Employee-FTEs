"""
Personal AI Employee - Bronze Tier

A foundational AI Employee that monitors a folder for new files,
captures them as tasks in an Obsidian vault, and generates actionable
plans using Claude AI.
"""

from setuptools import setup, find_packages

setup(
    name="ai-employee-bronze",
    version="1.0.0",
    description="Personal AI Employee - Bronze Tier",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.18.0",
        "watchdog>=4.0.0",
        "python-frontmatter>=1.0.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.0",
        "pyyaml>=6.0.0",
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
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
