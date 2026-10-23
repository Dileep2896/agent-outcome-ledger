from .models import AgentRun, GovernanceFlag, WorkContract


def check_run(contract: WorkContract, run: AgentRun) -> list[GovernanceFlag]:
    flags = []
    if run.cost_usd > contract.budget_usd_per_run:
        flags.append(
            GovernanceFlag(
                code="over_budget",
                reason=(
                    f"${run.cost_usd:.2f} spend exceeds the "
                    f"${contract.budget_usd_per_run:.2f} run budget."
                ),
            )
        )
    for index, step in enumerate(run.steps):
        if step.tool not in contract.allowed_systems:
            flags.append(
                GovernanceFlag(
                    code="tool_not_allowed",
                    step_index=index,
                    reason=f"{step.tool} is not allowed by this contract.",
                )
            )
        for rule in contract.human_checkpoints:
            if step.tool == rule.tool and step.args.get("amount", 0) > rule.when_amount_gt:
                timestamp = step.executed_at or run.started_at
                approved = any(
                    a.tool == step.tool
                    and a.approved_at < timestamp
                    and (a.step_index is None or a.step_index == index)
                    for a in run.approvals
                )
                if not approved:
                    flags.append(
                        GovernanceFlag(
                            code="missing_approval",
                            step_index=index,
                            reason=(
                                f"{step.tool} for ${step.args['amount']:.2f} "
                                "required human approval "
                                f"before this step (threshold ${rule.when_amount_gt:.0f})."
                            ),
                        )
                    )
    return flags
