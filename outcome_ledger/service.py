"""Compose pure calculations once per snapshot; API and CLI share this read model."""

from dataclasses import dataclass

from .allocate import build_plan, replay
from .attribution import attribute
from .gate import evaluate_gate
from .governance import check_run
from .metrics import run_samples, summarize
from .models import AttributionResult, GateDecision, GovernanceFlag, SeedData


@dataclass
class Ledger:
    data: SeedData
    attribution: AttributionResult
    naive: AttributionResult
    variants: list[dict]
    workflows: list[dict]
    gates: list[GateDecision]
    flags: dict[str, list[GovernanceFlag]]
    plan: list[dict]
    replay: dict
    totals: dict

    def summary(self) -> dict:
        return {
            "week": "2026-10-12",
            "as_of": self.data.as_of,
            "totals": self.totals,
            "coverage": {
                "naive": self.naive.coverage,
                "engine": self.attribution.coverage,
                "total_outcome_value": self.attribution.total_outcome_value,
                "naive_value": self.naive.attributed_value,
                "unmatched_count": len(self.attribution.unmatched),
            },
            "workflows": self.workflows,
            "variants": self.variants,
        }

    def impact(self) -> dict:
        before, after = self.replay["before_spend"], self.replay["after_spend"]
        return {
            "naive_coverage": self.naive.coverage,
            "engine_coverage": self.attribution.coverage,
            "before_value_per_dollar": self.replay["before_value"] / before if before else 0,
            "after_value_per_dollar": self.replay["after_value"] / after if after else 0,
            "flags_caught": sum(len(flags) for flags in self.flags.values()),
            "flagged_runs": sum(bool(flags) for flags in self.flags.values()),
            "runs": len(self.data.runs),
            "events": len(self.data.events),
            "spend": before,
            "tokens": sum(
                s.input_tokens + s.output_tokens for r in self.data.runs for s in r.steps
            ),
            "attributed_value": self.attribution.attributed_value,
            "replay": self.replay,
            "gates": self.gates,
            "label": "Measured on the demo's seed data",
        }


def build_ledger(data: SeedData) -> Ledger:
    result = attribute(data.contracts, data.runs, data.events)
    naive = attribute(data.contracts, data.runs, data.events, exact=True)
    variants, workflows, gates, flags = [], [], [], {}
    for contract in data.contracts:
        runs = [r for r in data.runs if r.contract_id == contract.id]
        workflows.append({"workflow": contract.workflow, **summarize(runs, result.credits)})
        for variant in ["incumbent", "challenger"]:
            selected = [r for r in runs if r.variant == variant]
            variants.append(
                {
                    "workflow": contract.workflow,
                    "variant": variant,
                    **summarize(selected, result.credits),
                }
            )
        gates.append(
            evaluate_gate(
                contract.workflow,
                run_samples([r for r in runs if r.variant == "challenger"], result.credits),
                run_samples([r for r in runs if r.variant == "incumbent"], result.credits),
            )
        )
        flags.update({run.id: check_run(contract, run) for run in runs})
    plan = build_plan(variants, gates)
    return Ledger(
        data,
        result,
        naive,
        variants,
        workflows,
        gates,
        flags,
        plan,
        replay(plan, variants),
        summarize(data.runs, result.credits),
    )
