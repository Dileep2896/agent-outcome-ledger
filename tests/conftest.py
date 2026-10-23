from datetime import UTC, datetime, timedelta

import pytest

from outcome_ledger.models import AgentRun, OutcomeEvent, Step, ValueSource, WorkContract

T0 = datetime(2026, 10, 12, tzinfo=UTC)


@pytest.fixture
def contract():
    return WorkContract(
        id="refund",
        workflow="Refund triage",
        owner="Mara Vale",
        success_event="resolved",
        negative_events=["reopened"],
        attribution_window_days=7,
        value_source=ValueSource(mode="fixed", fixed_usd=100),
        budget_usd_per_run=1,
        allowed_systems=["lookup_order", "issue_refund"],
        human_checkpoints=[{"tool": "issue_refund", "when_amount_gt": 200}],
        entity_key="ticket",
    )


@pytest.fixture
def run_factory():
    def make(id="r1", entity_ref="ticket:1", days=0, variant="incumbent", **kwargs):
        return AgentRun(
            id=id,
            contract_id="refund",
            variant=variant,
            entity_ref=entity_ref,
            started_at=T0 + timedelta(days=days),
            steps=kwargs.pop(
                "steps",
                [
                    Step(
                        tool="lookup_order",
                        model="reasoner-mini",
                        input_tokens=100_000,
                        output_tokens=10_000,
                    )
                ],
            ),
            **kwargs,
        )

    return make


@pytest.fixture
def event_factory():
    def make(id="e1", key="HS-1", days=2, type="resolved", **kwargs):
        return OutcomeEvent(
            id=id,
            source="helpdesk",
            type=type,
            external_key=key,
            occurred_at=T0 + timedelta(days=days),
            **kwargs,
        )

    return make
