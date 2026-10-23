import pytest
from pydantic import ValidationError

from outcome_ledger.attribution import attribute
from outcome_ledger.models import Step, WorkContract


def test_late_reversal_cannot_make_coverage_exceed_one(contract, run_factory, event_factory):
    events = [
        event_factory(),
        event_factory(id="e2", key="HS-99"),
        event_factory(id="e3", type="reopened", days=8),
    ]
    result = attribute([contract], [run_factory()], events)
    assert result.attributed_value == 100
    assert result.total_outcome_value == 200
    assert result.coverage == 0.5
    assert any(u.event.id == "e3" and u.reason == "outside_window" for u in result.unmatched)


def test_reversal_does_not_revive_expired_run(contract, run_factory, event_factory):
    runs = [run_factory(), run_factory(id="late", days=6)]
    events = [event_factory(), event_factory(id="e2", type="reopened", days=8)]
    result = attribute([contract], runs, events)
    assert result.attributed_value == 100
    assert not any(c.value_usd < 0 for c in result.credits)


def test_exact_baseline_has_same_denominator_as_engine(contract, run_factory, event_factory):
    events = [
        event_factory(key="ticket:1"),
        event_factory(id="e2", key="HS-1", type="reopened", days=8),
    ]
    normal = attribute([contract], [run_factory()], events)
    exact = attribute([contract], [run_factory()], events, exact=True)
    assert normal.total_outcome_value == exact.total_outcome_value == 100


@pytest.mark.parametrize(
    "field,value", [("input_tokens", -1), ("output_tokens", -1), ("model", "not-priced")]
)
def test_invalid_step_is_rejected(field, value):
    values = dict(tool="lookup_order", model="reasoner-mini", input_tokens=1, output_tokens=1)
    values[field] = value
    with pytest.raises(ValidationError):
        Step(**values)


def test_invalid_contract_window_is_rejected(contract):
    values = contract.model_dump()
    values["attribution_window_days"] = 0
    with pytest.raises(ValidationError):
        WorkContract(**values)
