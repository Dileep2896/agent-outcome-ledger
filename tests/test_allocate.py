import pytest

from outcome_ledger.allocate import bounded_shares, replay


@pytest.mark.parametrize("weights", [[1, 1, 1], [1000, 1, 0], [0, 0, 0], [-1, 0, 1], [4, 8, 12]])
def test_floor_cap_and_sum(weights):
    shares = bounded_shares(weights)
    assert sum(shares) == pytest.approx(1)
    assert all(0.1 - 1e-9 <= s <= 0.6 + 1e-9 for s in shares)


def test_budget_replay_conserves_spend():
    plan = [{"workflow": "A", "variant": "incumbent", "budget": 100}]
    ledger = [
        {"workflow": "A", "variant": "incumbent", "runs": 10, "spend": 50, "attributed_value": 200}
    ]
    result = replay(plan, ledger)
    assert result["after_spend"] == 100
    assert result["after_value"] == 400


def test_infeasible_bounds_fail():
    with pytest.raises(ValueError):
        bounded_shares([1])
