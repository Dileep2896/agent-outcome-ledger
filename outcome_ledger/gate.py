import math

from .metrics import Sample, bootstrap_difference, ratio
from .models import GateDecision


def evaluate_gate(
    workflow: str, challenger: list[Sample], incumbent: list[Sample], min_runs: int = 30
) -> GateDecision:
    low, high = bootstrap_difference(challenger, incumbent)
    delta = ratio(challenger) - ratio(incumbent)
    n = len(challenger)
    enough = n >= min_runs and len(incumbent) >= min_runs
    if enough and low > 0:
        verdict, chosen, needed = "PROMOTE", "challenger", 0
        reason = f"{n} challenger runs; the entire 90% advantage interval clears zero."
    elif enough and high < 0:
        verdict, chosen, needed = "ROLLBACK", "incumbent", 0
        reason = f"{n} challenger runs; even the upper 90% bound is below the incumbent."
    else:
        verdict, chosen = "HOLD", "incumbent"
        # Approximation: width shrinks as 1/sqrt(n), assuming the same effect and variance.
        # A near-zero effect has no finite useful estimate; request another minimum-size batch.
        half_width = (high - low) / 2
        target = (
            math.ceil(max(n, 1) * (half_width / abs(delta)) ** 2) + 1
            if abs(delta) > 1e-9
            else n + min_runs
        )
        needed = max(1, min_runs - n, target - n)
        reason = f"Only {n} challenger runs; " if n < min_runs else f"{n} challenger runs; "
        reason += (
            "the 90% interval crosses zero. "
            if low <= 0 <= high
            else "the minimum sample is not met. "
        )
        reason += (
            f"Estimate {needed} more challenger runs before reconsidering; keep the incumbent."
        )
    return GateDecision(
        workflow=workflow,
        verdict=verdict,
        chosen_variant=chosen,
        reason=reason,
        n_challenger=n,
        n_incumbent=len(incumbent),
        difference_interval=(low, high),
        difference=delta,
        runs_needed=needed,
    )
