from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, computed_field, field_validator

from .pricing import PRICES, token_cost


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ValueSource(Record):
    mode: Literal["fixed", "event_amount"]
    fixed_usd: float = Field(default=0, ge=0)


class HumanCheckpoint(Record):
    tool: str
    when_amount_gt: float = Field(ge=0)


class WorkContract(Record):
    id: str
    workflow: str
    owner: str
    success_event: str
    negative_events: list[str]
    attribution_window_days: int = Field(gt=0)
    value_source: ValueSource
    budget_usd_per_run: float = Field(gt=0)
    allowed_systems: list[str]
    human_checkpoints: list[HumanCheckpoint] = Field(default_factory=list)
    entity_key: Literal["ticket", "lead", "invoice"]


class Step(Record):
    tool: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    args: dict = Field(default_factory=dict)
    executed_at: AwareDatetime | None = None

    @field_validator("model")
    @classmethod
    def known_model(cls, value: str) -> str:
        if value not in PRICES:
            raise ValueError(f"Unknown model: {value}")
        return value

    @computed_field
    @property
    def cost_usd(self) -> float:
        return token_cost(self.model, self.input_tokens, self.output_tokens)


class Approval(Record):
    tool: str
    approved_at: AwareDatetime
    approver: str
    step_index: int | None = Field(default=None, ge=0)


class AgentRun(Record):
    id: str
    contract_id: str
    variant: Literal["incumbent", "challenger"]
    entity_ref: str
    started_at: AwareDatetime
    steps: list[Step]
    approvals: list[Approval] = Field(default_factory=list)

    @computed_field
    @property
    def cost_usd(self) -> float:
        return round(sum(step.cost_usd for step in self.steps), 8)


class OutcomeEvent(Record):
    id: str
    source: Literal["crm", "billing", "helpdesk"]
    type: str
    external_key: str
    occurred_at: AwareDatetime
    amount_usd: float | None = Field(default=None, ge=0)


class Credit(Record):
    run_id: str
    event_id: str
    value_usd: float
    explanation: str


class Unmatched(Record):
    event: OutcomeEvent
    reason: Literal["no_run", "outside_window", "unknown_key_format"]


class AttributionResult(Record):
    credits: list[Credit]
    unmatched: list[Unmatched]
    total_outcome_value: float

    @computed_field
    @property
    def attributed_value(self) -> float:
        return max(0, sum(credit.value_usd for credit in self.credits))

    @computed_field
    @property
    def coverage(self) -> float:
        return self.attributed_value / self.total_outcome_value if self.total_outcome_value else 0


class GovernanceFlag(Record):
    code: Literal["over_budget", "missing_approval", "tool_not_allowed"]
    reason: str
    step_index: int | None = None


class GateDecision(Record):
    workflow: str
    verdict: Literal["PROMOTE", "HOLD", "ROLLBACK"]
    reason: str
    n_challenger: int
    n_incumbent: int
    difference_interval: tuple[float, float]
    difference: float
    runs_needed: int
    chosen_variant: Literal["incumbent", "challenger"]


class SeedData(Record):
    contracts: list[WorkContract]
    runs: list[AgentRun]
    events: list[OutcomeEvent]
    as_of: datetime
