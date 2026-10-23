"""Constrained proportional allocation and fractional-run replay at observed unit economics."""

from .models import GateDecision


def bounded_shares(weights: list[float], floor: float = 0.1, cap: float = 0.6) -> list[float]:
    n = len(weights)
    if not n or floor < 0 or cap < floor or n * floor > 1 or n * cap < 1:
        raise ValueError("Infeasible allocation bounds")
    weights = [max(0.0, w) for w in weights]
    if not any(weights):
        return [1 / n] * n
    # Solve sum(clamp(lambda * weight, floor, cap)) = 1 by monotone bisection.
    # Tiny fallback weights keep the problem feasible when only one workflow has signal.
    weights = [max(w, max(weights) * 1e-12) for w in weights]
    low, high = 0.0, 1 / min(weights)
    for _ in range(160):
        middle = (low + high) / 2
        if sum(min(cap, max(floor, middle * w)) for w in weights) < 1:
            low = middle
        else:
            high = middle
    return [min(cap, max(floor, high * w)) for w in weights]


def build_plan(ledger: list[dict], gates: list[GateDecision]) -> list[dict]:
    total = sum(row["spend"] for row in ledger)
    chosen = [
        next(
            row
            for row in ledger
            if row["workflow"] == gate.workflow and row["variant"] == gate.chosen_variant
        )
        for gate in gates
    ]
    shares = bounded_shares([row["interval"][0] for row in chosen])
    budgets = [round(total * share, 8) for share in shares]
    budgets[-1] = total - sum(budgets[:-1])
    return [
        {
            "workflow": row["workflow"],
            "variant": row["variant"],
            "share": share,
            "budget": budget,
            "before_budget": sum(r["spend"] for r in ledger if r["workflow"] == row["workflow"]),
            "conservative_value_per_dollar": row["interval"][0],
        }
        for row, share, budget in zip(chosen, shares, budgets, strict=True)
    ]


def replay(plan: list[dict], ledger: list[dict]) -> dict:
    value = 0.0
    for allocation in plan:
        row = next(
            r
            for r in ledger
            if r["workflow"] == allocation["workflow"] and r["variant"] == allocation["variant"]
        )
        cost_per_run = row["spend"] / row["runs"] if row["runs"] else 0
        value_per_run = row["attributed_value"] / row["runs"] if row["runs"] else 0
        value += allocation["budget"] / cost_per_run * value_per_run if cost_per_run else 0
    return {
        "before_spend": sum(row["spend"] for row in ledger),
        "after_spend": sum(row["budget"] for row in plan),
        "before_value": sum(row["attributed_value"] for row in ledger),
        "after_value": value,
    }
