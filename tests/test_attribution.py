import pytest

from outcome_ledger.attribution import attribute, naive_join
from outcome_ledger.models import ValueSource
from outcome_ledger.normalize import NORMALIZERS


def test_normalized_credit_has_audit_trail(contract, run_factory, event_factory):
    result = attribute([contract], [run_factory()], [event_factory(days=2.1)], NORMALIZERS)
    assert result.attributed_value == 100
    assert result.coverage == 1
    assert "HS-1 → ticket:1, +2.1d, window 7d" in result.credits[0].explanation


@pytest.mark.parametrize(("days", "expected"), [(0, 100), (7, 100), (-0.01, 0), (7.01, 0)])
def test_window_is_inclusive(contract, run_factory, event_factory, days, expected):
    result = attribute([contract], [run_factory()], [event_factory(days=days)], NORMALIZERS)
    assert result.attributed_value == expected
    if not expected:
        assert result.unmatched[0].reason == "outside_window"


def test_split_credit_conserves_value(contract, run_factory, event_factory):
    result = attribute(
        [contract], [run_factory(), run_factory(id="r2", days=1)], [event_factory()], NORMALIZERS
    )
    assert [c.value_usd for c in result.credits] == [50, 50]
    assert result.attributed_value == 100


def test_negative_reverses_original_recipients_never_below_zero(
    contract, run_factory, event_factory
):
    events = [
        event_factory(),
        event_factory(id="e2", type="reopened", days=3),
        event_factory(id="e3", type="reopened", days=4),
    ]
    result = attribute(
        [contract],
        [run_factory(), run_factory(id="late", days=2.5)],
        list(reversed(events)),
        NORMALIZERS,
    )
    assert result.attributed_value == 0
    assert sum(c.value_usd for c in result.credits if c.run_id == "late") == 0
    assert sum(c.value_usd for c in result.credits if c.run_id == "r1") == 0


def test_negative_before_success_does_not_reverse_future(contract, run_factory, event_factory):
    result = attribute(
        [contract],
        [run_factory()],
        [event_factory(), event_factory(id="negative", type="reopened", days=1)],
        NORMALIZERS,
    )
    assert result.attributed_value == 100


@pytest.mark.parametrize(
    ("key", "days", "reason"),
    [("HS-99", 2, "no_run"), ("HS-1", 8, "outside_window"), ("broken", 2, "unknown_key_format")],
)
def test_unmatched_reasons(contract, run_factory, event_factory, key, days, reason):
    result = attribute(
        [contract], [run_factory()], [event_factory(key=key, days=days)], NORMALIZERS
    )
    assert result.unmatched[0].reason == reason
    assert result.total_outcome_value == 100


def test_amount_based_value(contract, run_factory, event_factory):
    contract.value_source = ValueSource(mode="event_amount")
    result = attribute([contract], [run_factory()], [event_factory(amount_usd=123.45)], NORMALIZERS)
    assert result.attributed_value == 123.45


def test_naive_only_matches_exact_keys(run_factory, event_factory):
    assert naive_join([run_factory()], [event_factory()]) == []
    assert naive_join([run_factory()], [event_factory(key="ticket:1")]) == [("r1", "e1")]


def test_unrelated_event_type_is_not_countable(contract, run_factory, event_factory):
    result = attribute(
        [contract], [run_factory()], [event_factory(type="email_opened")], NORMALIZERS
    )
    assert result.total_outcome_value == 0
    assert result.credits == []


def test_duplicate_event_id_is_idempotent(contract, run_factory, event_factory):
    event = event_factory()
    result = attribute([contract], [run_factory()], [event, event], NORMALIZERS)
    assert result.attributed_value == 100


def test_input_order_does_not_change_result(contract, run_factory, event_factory):
    runs = [run_factory(), run_factory(id="r2")]
    events = [event_factory(), event_factory(id="e2", days=3)]
    assert attribute([contract], runs, events, NORMALIZERS) == attribute(
        [contract], runs[::-1], events[::-1], NORMALIZERS
    )
