from datetime import timedelta

from outcome_ledger.governance import check_run
from outcome_ledger.models import Approval, Step


def refund_step(amount=250):
    return Step(
        tool="issue_refund",
        model="reasoner-mini",
        input_tokens=100,
        output_tokens=100,
        args={"amount": amount},
    )


def test_missing_approval(contract, run_factory):
    assert "missing_approval" in [
        f.code for f in check_run(contract, run_factory(steps=[refund_step()]))
    ]


def test_prior_approval_is_valid(contract, run_factory):
    run = run_factory(steps=[refund_step()])
    run.approvals = [
        Approval(
            tool="issue_refund",
            approved_at=run.started_at - timedelta(seconds=1),
            approver="Mara Vale",
        )
    ]
    assert check_run(contract, run) == []


def test_late_approval_does_not_count(contract, run_factory):
    run = run_factory(steps=[refund_step()])
    run.approvals = [
        Approval(
            tool="issue_refund",
            approved_at=run.started_at + timedelta(seconds=1),
            approver="Mara Vale",
        )
    ]
    assert check_run(contract, run)[0].code == "missing_approval"


def test_checkpoint_threshold_is_strict(contract, run_factory):
    assert check_run(contract, run_factory(steps=[refund_step(200)])) == []


def test_disallowed_tool(contract, run_factory):
    step = refund_step()
    step.tool = "delete_account"
    assert check_run(contract, run_factory(steps=[step]))[0].code == "tool_not_allowed"


def test_over_budget(contract, run_factory):
    contract.budget_usd_per_run = 0.01
    assert check_run(contract, run_factory())[0].code == "over_budget"
