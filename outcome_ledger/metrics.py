"""Run-level bootstrap, 2,000 seeded resamples; intervals describe associations, not causality."""

import random
from collections import defaultdict

from .models import AgentRun, Credit

Sample = tuple[float, float]  # spend, net attributed value


def ratio(samples: list[Sample]) -> float:
    spend = sum(s[0] for s in samples)
    return sum(s[1] for s in samples) / spend if spend else 0


def interval(values: list[float]) -> tuple[float, float]:
    values.sort()
    return (values[int((len(values) - 1) * 0.05)], values[int((len(values) - 1) * 0.95)])


def bootstrap_ratio(samples: list[Sample], seed: int = 42, resamples: int = 2000):
    if not samples:
        return (0.0, 0.0)
    rng = random.Random(seed)
    return interval([ratio(rng.choices(samples, k=len(samples))) for _ in range(resamples)])


def bootstrap_difference(
    challenger: list[Sample], incumbent: list[Sample], seed: int = 42, resamples: int = 2000
):
    if not challenger or not incumbent:
        return (0.0, 0.0)
    rng = random.Random(seed)
    return interval(
        [
            ratio(rng.choices(challenger, k=len(challenger)))
            - ratio(rng.choices(incumbent, k=len(incumbent)))
            for _ in range(resamples)
        ]
    )


def run_samples(runs: list[AgentRun], credits: list[Credit]) -> list[Sample]:
    values: dict[str, float] = defaultdict(float)
    for credit in credits:
        values[credit.run_id] += credit.value_usd
    return [(run.cost_usd, max(0, values[run.id])) for run in sorted(runs, key=lambda r: r.id)]


def summarize(runs: list[AgentRun], credits: list[Credit]) -> dict:
    samples = run_samples(runs, credits)
    spend = sum(s[0] for s in samples)
    value = sum(s[1] for s in samples)
    successes = sum(s[1] > 0 for s in samples)
    return {
        "runs": len(runs),
        "spend": spend,
        "attributed_value": value,
        "successes": successes,
        "success_rate": successes / len(runs) if runs else 0,
        "value_per_dollar": value / spend if spend else 0,
        "cost_per_success": spend / successes if successes else None,
        "interval": bootstrap_ratio(samples),
    }
