import pytest

from outcome_ledger.seed import make_seed
from outcome_ledger.service import build_ledger
from outcome_ledger.sources import MockBilling, MockCRM, MockHelpdesk


@pytest.fixture(scope="module")
def ledger():
    return build_ledger(make_seed())


def test_seed_is_deterministic():
    assert make_seed() == make_seed()


def test_seed_volume(ledger):
    assert len(ledger.data.runs) == 240
    assert 180 <= len(ledger.data.events) <= 220


def test_coverage_ranges(ledger):
    assert 0.25 <= ledger.naive.coverage <= 0.45
    assert 0.90 <= ledger.attribution.coverage <= 1


def test_all_unmatched_reasons(ledger):
    assert {u.reason for u in ledger.attribution.unmatched} == {
        "no_run",
        "outside_window",
        "unknown_key_format",
    }


def test_gate_verdicts(ledger):
    assert {g.workflow: g.verdict for g in ledger.gates} == {
        "Refund triage": "HOLD",
        "Lead qualification": "PROMOTE",
        "Invoice dunning": "ROLLBACK",
    }


def test_small_sample_is_noisy_and_looks_twice_as_good(ledger):
    gate = next(g for g in ledger.gates if g.workflow == "Refund triage")
    assert gate.n_challenger == 11
    assert gate.difference_interval[0] < 0 < gate.difference_interval[1]
    rows = {r["variant"]: r for r in ledger.variants if r["workflow"] == gate.workflow}
    point_ratio = rows["challenger"]["value_per_dollar"] / rows["incumbent"]["value_per_dollar"]
    assert 1.7 < point_ratio < 2.5


def test_missing_approvals_and_overruns(ledger):
    codes = [flag.code for flags in ledger.flags.values() for flag in flags]
    assert codes.count("missing_approval") == 5
    assert 2 <= codes.count("over_budget") <= 10


def test_plan_preserves_budget_and_improves_seed_replay(ledger):
    assert ledger.replay["before_spend"] == pytest.approx(ledger.replay["after_spend"])
    assert ledger.replay["after_value"] > ledger.replay["before_value"]
    assert all(0.1 <= row["share"] <= 0.6 for row in ledger.plan)


def test_mock_sources_respect_time_range(ledger):
    for cls, name in [(MockCRM, "crm"), (MockBilling, "billing"), (MockHelpdesk, "helpdesk")]:
        source = cls(ledger.data.events)
        items = source.fetch(ledger.data.runs[0].started_at, ledger.data.as_of)
        assert items and all(e.source == name for e in items)
        assert source.fetch(ledger.data.as_of, ledger.data.as_of) == []
