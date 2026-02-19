"""
Integration test for approval workflow (Silver Tier)

Tests the complete approval workflow:
1. Task creation
2. Reasoning skill generates plan with approval requirement
3. Approval skill creates approval request in Waiting_Approval/
4. Human approves via APPROVED.txt
5. Approval skill moves to Approved/
"""

from pathlib import Path
from ai_employee.config import Config
from ai_employee.models.task import Task
from ai_employee.skills.reasoning_skill import ReasoningSkill
from ai_employee.skills.approval_skill import ApprovalSkill


def test_approval_workflow():
    """Test complete approval workflow"""
    print("=" * 60)
    print("Testing Silver Tier Approval Workflow")
    print("=" * 60)

    config = Config()
    reasoning_skill = ReasoningSkill(vault_path=config.vault_path)
    approval_skill = ApprovalSkill(vault_path=config.vault_path)

    # Step 1: Create task that requires approval
    print("\n[Step 1] Creating task that requires approval...")
    task = Task(
        title="Send email to client about payment",
        content="Send an email to client@example.com requesting payment of $5000 for invoice #12345. Due date is March 1st.",
        source="gmail",
    )
    print(f"Task ID: {task.id}")
    print(f"Task: {task.title}")

    # Step 2: Generate plan with reasoning skill
    print("\n[Step 2] Generating plan with reasoning skill...")
    plan, needs_approval = reasoning_skill.generate_plan(task)
    print(f"Needs approval: {needs_approval}")
    print(f"Steps: {len(plan.steps)}")
    print(f"Approval checkpoints: {plan.approval_checkpoints}")
    print(f"Warnings: {len(plan.warnings)}")

    # Step 3: Create approval request if needed
    if needs_approval:
        print("\n[Step 3] Creating approval request...")
        approval_path = approval_skill.create_approval_request(task, plan)
        print(f"Approval request created: {approval_path}")

        # Show approval request content
        print("\n[Approval Request Content]")
        print("-" * 60)
        print(approval_path.read_text(encoding="utf-8")[:500] + "...")
        print("-" * 60)

        # Step 4: Simulate human approval
        print("\n[Step 4] Simulating human approval...")
        approved_file = config.vault_path / "Waiting_Approval" / "APPROVED.txt"
        approved_file.write_text("Approved by human", encoding="utf-8")
        print(f"Created: {approved_file}")

        # Step 5: Process pending approvals
        print("\n[Step 5] Processing pending approvals...")
        results = approval_skill.process_pending_approvals()
        print(f"Results: {results}")

        # Step 6: Verify task moved to Approved/
        print("\n[Step 6] Verifying task moved to Approved/...")
        approved_folder = config.vault_path / "Approved"
        approved_files = list(approved_folder.glob("approval-*.md"))
        print(f"Files in Approved/: {len(approved_files)}")

        if approved_files:
            print(f"[OK] Task successfully approved and moved to Approved/")
            print(f"  File: {approved_files[-1].name}")
        else:
            print(f"[FAIL] Task not found in Approved/")

        # Check Waiting_Approval is empty
        waiting_folder = config.vault_path / "Waiting_Approval"
        waiting_files = list(waiting_folder.glob("approval-*.md"))
        print(f"Files in Waiting_Approval/: {len(waiting_files)}")

        if len(waiting_files) == 0:
            print(f"[OK] Waiting_Approval/ folder is clean")
        else:
            print(f"[FAIL] Waiting_Approval/ still has files")

    print("\n" + "=" * 60)
    print("Approval Workflow Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_approval_workflow()
