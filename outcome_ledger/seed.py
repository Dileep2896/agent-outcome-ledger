"""Fictional weekly operations, generated deterministically with random.Random(42)."""

import random
from datetime import UTC, datetime, timedelta

from .models import AgentRun, Approval, OutcomeEvent, SeedData, Step, ValueSource, WorkContract

NOW = datetime(2026, 10, 19, tzinfo=UTC)
WEEK = datetime(2026, 10, 12, tzinfo=UTC)


def make_seed() -> SeedData:
    rng = random.Random(42)
    contracts = [
        WorkContract(
            id="refund",
            workflow="Refund triage",
            owner="Mara Vale",
            success_event="refund_resolved",
            negative_events=["ticket_reopened"],
            attribution_window_days=7,
            value_source=ValueSource(mode="event_amount"),
            budget_usd_per_run=0.55,
            entity_key="ticket",
            allowed_systems=["lookup_order", "issue_refund"],
            human_checkpoints=[{"tool": "issue_refund", "when_amount_gt": 200}],
        ),
        WorkContract(
            id="lead",
            workflow="Lead qualification",
            owner="Ari Rowan",
            success_event="lead_qualified",
            negative_events=["lead_disqualified"],
            attribution_window_days=4,
            value_source=ValueSource(mode="fixed", fixed_usd=200),
            budget_usd_per_run=1.1,
            entity_key="lead",
            allowed_systems=["enrich_lead", "update_crm", "send_email"],
        ),
        WorkContract(
            id="invoice",
            workflow="Invoice dunning",
            owner="Soren Pike",
            success_event="invoice_paid",
            negative_events=["refund_chargeback"],
            attribution_window_days=3,
            value_source=ValueSource(mode="event_amount"),
            budget_usd_per_run=1.4,
            entity_key="invoice",
            allowed_systems=["fetch_invoice", "schedule_reminder", "send_email"],
        ),
    ]
    runs, events = [], []
    source_for = {"refund": "helpdesk", "lead": "crm", "invoice": "billing"}
    for contract in contracts:
        for variant in ["incumbent", "challenger"]:
            count = (69 if variant == "incumbent" else 11) if contract.id == "refund" else 40
            successes = {"refund": (49, 4), "lead": (24, 38), "invoice": (38, 30)}[contract.id][
                variant == "challenger"
            ]
            for index in range(count):
                serial = index + (100 if variant == "challenger" else 0)
                entity_id = 10293 + serial if contract.id == "refund" else 417 + serial
                email = f"contact.{serial}@coppergrove.example"
                entity = {
                    "refund": f"ticket:{entity_id}",
                    "lead": f"lead:{email}",
                    "invoice": f"invoice:{entity_id}",
                }[contract.id]
                external = {
                    "refund": f"HS-{entity_id}",
                    "lead": email.replace("@", "+demo@").title(),
                    "invoice": f"INV-2026-{entity_id:05d}",
                }[contract.id]
                started = WEEK + timedelta(days=index % 4, hours=rng.randrange(8, 17))
                tools = contract.allowed_systems[:2]
                model = (
                    "reasoner-pro"
                    if (contract.id == "lead" and variant == "incumbent")
                    or (contract.id == "invoice" and variant == "challenger")
                    else "reasoner-mini"
                )
                multiplier = 4 if contract.id == "refund" and index in (8, 21) else 1
                steps = [
                    Step(
                        tool=tool,
                        model=model,
                        input_tokens=int(rng.randint(65_000, 85_000) * multiplier),
                        output_tokens=int(rng.randint(8_000, 12_000) * multiplier),
                        args=(
                            {"amount": 250 if index < 5 else 80}
                            if tool == "issue_refund"
                            else {"entity": entity}
                        ),
                        executed_at=started + timedelta(seconds=12 * (j + 1)),
                    )
                    for j, tool in enumerate(tools)
                ]
                if contract.id == "lead" and index == 39:
                    steps.append(
                        Step(
                            tool="export_contacts",
                            model=model,
                            input_tokens=100,
                            output_tokens=10,
                            executed_at=started + timedelta(seconds=40),
                        )
                    )
                approvals = []
                if contract.id == "refund" and index < 5 and variant == "challenger":
                    approvals = [
                        Approval(
                            tool="issue_refund",
                            approved_at=started,
                            approver="Mara Vale",
                            step_index=1,
                        )
                    ]
                run = AgentRun(
                    id=f"{contract.id}-{variant[0]}-{index + 1:03d}",
                    contract_id=contract.id,
                    variant=variant,
                    entity_ref=entity,
                    started_at=started,
                    steps=steps,
                    approvals=approvals,
                )
                runs.append(run)
                if index < successes:
                    amount = (
                        float(rng.randint(20, 34))
                        if contract.id == "refund"
                        else float(rng.randint(35, 85))
                    )
                    if contract.id == "refund" and variant == "challenger":
                        amount = 380 if index == 0 else 10
                    events.append(
                        OutcomeEvent(
                            id=f"out-{run.id}",
                            source=source_for[contract.id],
                            type=contract.success_event,
                            external_key=entity if index % 3 == 0 else external,
                            occurred_at=started + timedelta(days=2.1),
                            amount_usd=amount,
                        )
                    )
    # In-window reversals of earlier successes, using the same source key.
    for run_id in ["refund-i-005", "refund-i-009", "invoice-c-006"]:
        event = next(e for e in events if e.id == f"out-{run_id}")
        events.append(
            event.model_copy(
                update={
                    "id": f"reverse-{run_id}",
                    "type": ("ticket_reopened" if "refund" in run_id else "refund_chargeback"),
                    "occurred_at": event.occurred_at + timedelta(hours=12),
                }
            )
        )
    # Visible audit gaps. Every event is observable by NOW, including an expired 3-day window.
    for index in range(3):
        for suffix, key in [
            ("orphan", f"INV-2026-{99000 + index}"),
            ("invalid", f"legacy/{index}"),
            ("late", f"invoice:{417 + index * 4}"),
        ]:
            events.append(
                OutcomeEvent(
                    id=f"unmatched-{suffix}-{index}",
                    source="billing",
                    type="invoice_paid",
                    external_key=key,
                    occurred_at=WEEK + timedelta(days=5, hours=18),
                    amount_usd=25,
                )
            )
    return SeedData(contracts=contracts, runs=runs, events=events, as_of=NOW)
