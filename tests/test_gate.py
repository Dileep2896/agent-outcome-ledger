from outcome_ledger.gate import evaluate_gate


def test_promotes_clear_advantage():
    gate = evaluate_gate("w", [(1, 20)] * 40, [(1, 10)] * 40)
    assert gate.verdict == "PROMOTE"
    assert gate.runs_needed == 0
    assert gate.difference_interval[0] > 0


def test_rolls_back_clear_regression():
    assert evaluate_gate("w", [(1, 5)] * 40, [(1, 10)] * 40).verdict == "ROLLBACK"


def test_holds_small_sample_even_with_advantage():
    gate = evaluate_gate("w", [(1, 20)] * 11, [(1, 10)] * 40)
    assert gate.verdict == "HOLD"
    assert gate.runs_needed >= 19
    assert gate.reason


def test_holds_uncertain_sample():
    gate = evaluate_gate("w", [(1, 0), (1, 25)] * 20, [(1, 10)] * 40)
    assert gate.verdict == "HOLD"
    assert gate.runs_needed > 0


def test_empty_gate_holds():
    assert evaluate_gate("w", [], []).verdict == "HOLD"


def test_minimum_run_threshold_applies_to_both_arms():
    gate = evaluate_gate("w", [(1, 20)] * 30, [(1, 10)] * 30)
    assert gate.verdict == "PROMOTE"


def test_gate_holds_when_incumbent_sample_is_too_small():
    challenger = [(1.0, 10.0)] * 40
    incumbent = [(1.0, 1.0)] * 5
    decision = evaluate_gate("Lead qualification", challenger, incumbent)
    assert decision.verdict == "HOLD"
    assert decision.chosen_variant == "incumbent"
