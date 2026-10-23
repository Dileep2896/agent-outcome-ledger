"""Pure attribution. Equal split across eligible runs; reversals follow original recipients.

Coverage uses net countable value (successes less prior entity value reversed), including
unmatched outcomes in the denominator. Unrelated event types are excluded. Duplicate event
IDs are ingested once. The baseline joins successes by exact keys; both views apply
the same normalized reversal policy so reversed value cannot inflate baseline coverage.
An expired reversal stays unmatched and changes neither credit nor the denominator.
"""

from collections import defaultdict
from collections.abc import Callable
from datetime import timedelta

from .models import AgentRun, AttributionResult, Credit, OutcomeEvent, Unmatched, WorkContract
from .normalize import NORMALIZERS, normalize_entity

SOURCE_ENTITY = {"helpdesk": "ticket", "crm": "lead", "billing": "invoice"}


def naive_join(runs: list[AgentRun], events: list[OutcomeEvent]) -> list[tuple[str, str]]:
    return sorted({(r.id, e.id) for r in runs for e in events if r.entity_ref == e.external_key})


def attribute(
    contracts: list[WorkContract],
    runs: list[AgentRun],
    events: list[OutcomeEvent],
    normalizers: dict[str, Callable[[str], str | None]] | None = None,
    *,
    exact: bool = False,
) -> AttributionResult:
    normalizers = NORMALIZERS if normalizers is None else normalizers
    credits, unmatched = [], []
    balances: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    outcome_balances: dict[tuple[str, str], float] = defaultdict(float)
    runs_by_id = {r.id: r for r in runs}
    seen = set()
    for event in sorted(events, key=lambda e: (e.occurred_at, e.id)):
        if event.id in seen:
            continue
        seen.add(event.id)
        relevant = [
            c
            for c in contracts
            if c.entity_key == SOURCE_ENTITY[event.source]
            and event.type in [c.success_event, *c.negative_events]
        ]
        normalizer = normalizers.get(event.source)
        canonical = normalizer(event.external_key) if normalizer else None
        for contract in sorted(relevant, key=lambda c: c.id):
            account = (contract.id, canonical or event.external_key)
            success = event.type == contract.success_event
            value = (
                contract.value_source.fixed_usd
                if contract.value_source.mode == "fixed"
                else event.amount_usd or 0
            )
            if success:
                outcome_balances[account] += value
            exact_success = exact and success
            key = event.external_key if exact_success else canonical
            if key is None:
                unmatched.append(Unmatched(event=event, reason="unknown_key_format"))
                continue
            same_entity = [
                r
                for r in runs
                if r.contract_id == contract.id
                and (r.entity_ref if exact_success else normalize_entity(r.entity_ref)) == key
            ]
            eligible = sorted(
                [
                    r
                    for r in same_entity
                    if r.started_at
                    <= event.occurred_at
                    <= r.started_at + timedelta(days=contract.attribution_window_days)
                ],
                key=lambda r: r.id,
            )
            if not eligible:
                unmatched.append(
                    Unmatched(event=event, reason=("outside_window" if same_entity else "no_run"))
                )
                continue
            if success:
                allocations = {r.id: value / len(eligible) for r in eligible}
            else:
                # Reverse original recipients, never assign negative value to a later run.
                eligible_ids = {r.id for r in eligible}
                allocations = {
                    run_id: -balance
                    for run_id, balance in balances[account].items()
                    if balance > 0 and run_id in eligible_ids
                }
                if not allocations and any(v > 0 for v in balances[account].values()):
                    unmatched.append(Unmatched(event=event, reason="outside_window"))
                outcome_balances[account] += sum(allocations.values())
            for run_id, amount in sorted(allocations.items()):
                balances[account][run_id] += amount
                days = (event.occurred_at - runs_by_id[run_id].started_at).total_seconds() / 86400
                explanation = (
                    f"{event.source} {event.external_key} → {canonical or key}, "
                    f"+{days:.1f}d, window {contract.attribution_window_days}d"
                )
                if not success:
                    explanation += "; reverses prior entity credit"
                elif len(eligible) > 1:
                    explanation += f"; equal split across {len(eligible)} runs"
                credits.append(
                    Credit(
                        run_id=run_id, event_id=event.id, value_usd=amount, explanation=explanation
                    )
                )
    denominator = sum(outcome_balances.values())
    if exact:
        denominator = attribute(contracts, runs, events, normalizers).total_outcome_value
    return AttributionResult(credits=credits, unmatched=unmatched, total_outcome_value=denominator)
