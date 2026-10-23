import pytest

from outcome_ledger.metrics import bootstrap_difference, bootstrap_ratio, summarize
from outcome_ledger.models import Credit, Step
from outcome_ledger.pricing import token_cost


def test_pricing_uses_tokens():
    assert token_cost("reasoner-mini", 1_000_000, 1_000_000) == 5


def test_cost_is_computed_not_mutable(run_factory):
    run = run_factory(
        steps=[
            Step(
                tool="lookup_order", model="reasoner-mini", input_tokens=1_000_000, output_tokens=0
            )
        ]
    )
    assert run.cost_usd == 1


def test_unknown_model_fails():
    with pytest.raises(ValueError):
        token_cost("missing-model", 100, 100)


def test_bootstrap_reproducible():
    samples = [(1, 0), (1, 100), (2, 20)]
    assert bootstrap_ratio(samples, seed=42) == bootstrap_ratio(samples, seed=42)


def test_constant_ratio_has_zero_width():
    assert bootstrap_ratio([(2, 10)] * 10) == (5, 5)


def test_difference_direction():
    assert bootstrap_difference([(1, 10)] * 30, [(1, 5)] * 30) == (5, 5)


def test_empty_bootstrap_is_zero():
    assert bootstrap_ratio([]) == (0, 0)


def test_metrics_net_reversals_and_no_success(run_factory):
    run = run_factory()
    credits = [
        Credit(run_id=run.id, event_id="e1", value_usd=100, explanation="success"),
        Credit(run_id=run.id, event_id="e2", value_usd=-100, explanation="reversal"),
    ]
    metrics = summarize([run], credits)
    assert metrics["attributed_value"] == 0
    assert metrics["success_rate"] == 0
    assert metrics["cost_per_success"] is None
    assert metrics["spend"] == pytest.approx(run.cost_usd)
