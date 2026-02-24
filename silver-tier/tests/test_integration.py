#!/usr/bin/env python3
"""
Silver Tier Integration Test

Verifies all components are properly integrated and working.
Run this before setting up the scheduler to ensure everything is ready.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    """Print section header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text: str):
    """Print info message."""
    print(f"   {text}")


def test_imports() -> Tuple[bool, List[str]]:
    """Test that all required modules can be imported."""
    print_header("TEST 1: Module Imports")

    errors = []
    modules = [
        ("ai_employee.config", "Config"),
        ("ai_employee.runner", "AIEmployeeRunner"),
        ("ai_employee.watchers.file_watcher", "FileWatcher"),
        ("ai_employee.watchers.gmail_watcher", "GmailWatcher"),
        ("ai_employee.skills.reasoning_skill", "ReasoningSkill"),
        ("ai_employee.skills.approval_skill", "ApprovalSkill"),
        ("ai_employee.skills.linkedin_post_skill", "LinkedInPostSkill"),
        ("ai_employee.skills.linkedin_execution_skill", "LinkedInExecutionSkill"),
        ("ai_employee.mcp.mcp_server", "MCPServer"),
        ("ai_employee.models.task", "Task"),
        ("ai_employee.models.plan", "Plan"),
    ]

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_success(f"{module_name}.{class_name}")
        except ImportError as e:
            errors.append(f"Failed to import {module_name}: {e}")
            print_error(f"{module_name}.{class_name}: {e}")
        except AttributeError as e:
            errors.append(f"Class {class_name} not found in {module_name}: {e}")
            print_error(f"{module_name}.{class_name}: {e}")

    if not errors:
        print_success("All modules imported successfully")
        return True, []
    else:
        print_error(f"Failed to import {len(errors)} modules")
        return False, errors


def test_vault_structure() -> Tuple[bool, List[str]]:
    """Test that vault directory structure exists."""
    print_header("TEST 2: Vault Structure")

    from ai_employee.config import Config

    config = Config()
    vault_path = config.vault_path

    errors = []
    required_folders = [
        "Inbox",
        "Needs_Action",
        "Plans",
        "Waiting_Approval",
        "Approved",
        "Rejected",
        "LinkedIn_Posts",
        "Done",
    ]

    if not vault_path.exists():
        errors.append(f"Vault not found at {vault_path}")
        print_error(f"Vault not found at {vault_path}")
        print_info("Run: python -m ai_employee init")
        return False, errors

    print_success(f"Vault found at {vault_path}")

    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            print_success(f"{folder}/")
        else:
            print_warning(f"{folder}/ (will be created automatically)")

    return True, []


def test_configuration() -> Tuple[bool, List[str]]:
    """Test configuration and environment variables."""
    print_header("TEST 3: Configuration")

    from ai_employee.config import Config
    import os

    config = Config()
    errors = []
    warnings = []

    # Check vault path
    if config.vault_path.exists():
        print_success(f"Vault path: {config.vault_path}")
    else:
        errors.append(f"Vault path not found: {config.vault_path}")
        print_error(f"Vault path not found: {config.vault_path}")

    # Check LinkedIn credentials
    if config.linkedin_client_id and config.linkedin_client_secret:
        print_success("LinkedIn credentials configured")
    else:
        warnings.append("LinkedIn credentials not configured")
        print_warning("LinkedIn credentials not configured")
        print_info("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")

    # Check Gmail credentials (optional)
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if gmail_email and gmail_password:
        print_success("Gmail credentials configured")
    else:
        print_warning("Gmail credentials not configured (optional)")
        print_info("Set GMAIL_EMAIL and GMAIL_PASSWORD in .env for Gmail watcher")

    if errors:
        return False, errors
    else:
        if warnings:
            print_info(f"\n{len(warnings)} warnings (non-critical)")
        return True, []


def test_skills() -> Tuple[bool, List[str]]:
    """Test that skills can be instantiated."""
    print_header("TEST 4: Agent Skills")

    from ai_employee.config import Config
    from ai_employee.skills.reasoning_skill import ReasoningSkill
    from ai_employee.skills.approval_skill import ApprovalSkill
    from ai_employee.skills.linkedin_execution_skill import LinkedInExecutionSkill

    config = Config()
    errors = []

    try:
        reasoning = ReasoningSkill(vault_path=config.vault_path)
        print_success("ReasoningSkill initialized")
    except Exception as e:
        errors.append(f"ReasoningSkill failed: {e}")
        print_error(f"ReasoningSkill: {e}")

    try:
        approval = ApprovalSkill(vault_path=config.vault_path)
        print_success("ApprovalSkill initialized")
    except Exception as e:
        errors.append(f"ApprovalSkill failed: {e}")
        print_error(f"ApprovalSkill: {e}")

    try:
        linkedin = LinkedInExecutionSkill(vault_path=config.vault_path)
        print_success("LinkedInExecutionSkill initialized")
    except Exception as e:
        errors.append(f"LinkedInExecutionSkill failed: {e}")
        print_error(f"LinkedInExecutionSkill: {e}")

    if errors:
        return False, errors
    else:
        print_success("All skills initialized successfully")
        return True, []


def test_runner() -> Tuple[bool, List[str]]:
    """Test that runner can be instantiated."""
    print_header("TEST 5: AI Employee Runner")

    from ai_employee.config import Config
    from ai_employee.runner import AIEmployeeRunner

    config = Config()
    errors = []

    try:
        runner = AIEmployeeRunner(config)
        print_success("AIEmployeeRunner initialized")
        print_info(f"Vault: {runner.vault_path}")
        print_info(f"Watch folder: {config.watch_folder}")
    except Exception as e:
        errors.append(f"AIEmployeeRunner failed: {e}")
        print_error(f"AIEmployeeRunner: {e}")
        return False, errors

    return True, []


def test_mcp_server() -> Tuple[bool, List[str]]:
    """Test that MCP server can be instantiated."""
    print_header("TEST 6: MCP Server")

    from ai_employee.config import Config
    from ai_employee.mcp.mcp_server import MCPServer

    config = Config()
    errors = []

    try:
        mcp = MCPServer(vault_path=config.vault_path, use_mcp_client=False)
        print_success("MCPServer initialized")

        tools = mcp.list_tools()
        print_info(f"Available tools: {len(tools)}")
        for tool in tools:
            print_info(f"  - {tool['name']}: {tool['description'][:50]}...")

    except Exception as e:
        errors.append(f"MCPServer failed: {e}")
        print_error(f"MCPServer: {e}")
        return False, errors

    return True, []


def test_linkedin_oauth() -> Tuple[bool, List[str]]:
    """Test LinkedIn OAuth status."""
    print_header("TEST 7: LinkedIn OAuth")

    from ai_employee.skills.linkedin_post_skill import LinkedInPostSkill

    errors = []
    warnings = []

    try:
        linkedin = LinkedInPostSkill()

        if linkedin.is_authenticated():
            print_success("LinkedIn authenticated")
            print_info(f"Person URN: {linkedin.person_urn}")
        else:
            warnings.append("LinkedIn not authenticated")
            print_warning("LinkedIn not authenticated")
            print_info("Run: python -m ai_employee.skills.linkedin_post_skill")
            print_info("Follow OAuth flow in browser")

    except ValueError as e:
        warnings.append(f"LinkedIn credentials not configured: {e}")
        print_warning(f"LinkedIn credentials not configured")
        print_info("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")
    except Exception as e:
        errors.append(f"LinkedIn OAuth test failed: {e}")
        print_error(f"LinkedIn OAuth: {e}")

    if errors:
        return False, errors
    else:
        if warnings:
            print_info(f"\n{len(warnings)} warnings (setup required)")
        return True, []


def main():
    """Run all integration tests."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}SILVER TIER INTEGRATION TEST{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    tests = [
        ("Module Imports", test_imports),
        ("Vault Structure", test_vault_structure),
        ("Configuration", test_configuration),
        ("Agent Skills", test_skills),
        ("AI Employee Runner", test_runner),
        ("MCP Server", test_mcp_server),
        ("LinkedIn OAuth", test_linkedin_oauth),
    ]

    results = []
    all_errors = []

    for test_name, test_func in tests:
        try:
            success, errors = test_func()
            results.append((test_name, success))
            if errors:
                all_errors.extend(errors)
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))
            all_errors.append(f"{test_name} crashed: {e}")

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{BLUE}{'=' * 60}{RESET}")
    if passed == total:
        print(f"{GREEN}✅ ALL TESTS PASSED ({passed}/{total}){RESET}")
        print(f"\n{GREEN}Ready to setup OS scheduler!{RESET}")
        print(f"{BLUE}Run: .\\scripts\\setup_windows_scheduler.ps1{RESET}")
    else:
        print(f"{RED}❌ SOME TESTS FAILED ({passed}/{total}){RESET}")
        print(f"\n{RED}Fix errors before setting up scheduler{RESET}")
        if all_errors:
            print(f"\n{RED}Errors:{RESET}")
            for error in all_errors:
                print(f"  - {error}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
