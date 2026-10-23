export type Variant = 'incumbent' | 'challenger';
export interface Metrics {
  runs: number;
  spend: number;
  attributed_value: number;
  successes: number;
  success_rate: number;
  value_per_dollar: number;
  cost_per_success: number | null;
  interval: [number, number];
}
export interface VariantMetrics extends Metrics {
  workflow: string;
  variant: Variant;
}
export interface Summary {
  week: string;
  as_of: string;
  totals: Metrics;
  coverage: {
    naive: number;
    engine: number;
    total_outcome_value: number;
    naive_value: number;
    unmatched_count: number;
  };
  workflows: (Metrics & { workflow: string })[];
  variants: VariantMetrics[];
}
export interface GateDecision {
  workflow: string;
  verdict: 'PROMOTE' | 'HOLD' | 'ROLLBACK';
  reason: string;
  n_challenger: number;
  n_incumbent: number;
  difference_interval: [number, number];
  difference: number;
  runs_needed: number;
  chosen_variant: Variant;
}
export interface Replay {
  before_spend: number;
  after_spend: number;
  before_value: number;
  after_value: number;
}
export interface Allocation {
  workflow: string;
  variant: Variant;
  share: number;
  budget: number;
  before_budget: number;
  conservative_value_per_dollar: number;
}
export interface Plan {
  allocations: Allocation[];
  replay: Replay;
}
export interface Impact {
  naive_coverage: number;
  engine_coverage: number;
  before_value_per_dollar: number;
  after_value_per_dollar: number;
  flags_caught: number;
  flagged_runs: number;
  runs: number;
  events: number;
  spend: number;
  tokens: number;
  attributed_value: number;
  replay: Replay;
  gates: GateDecision[];
  label: string;
}
export interface Flag {
  code: string;
  reason: string;
  step_index: number | null;
}
export interface Credit {
  run_id: string;
  event_id: string;
  value_usd: number;
  explanation: string;
}
export interface Step {
  tool: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  args: Record<string, unknown>;
  executed_at: string | null;
}
export interface Outcome {
  id: string;
  source: string;
  type: string;
  external_key: string;
  occurred_at: string;
  amount_usd: number | null;
}
export interface Run {
  id: string;
  workflow: string;
  variant: Variant;
  entity_ref: string;
  started_at: string;
  cost_usd: number;
  attributed_value: number;
  flags: Flag[];
  steps: Step[];
  credits: Credit[];
}
export interface RunDetail extends Run {
  contract: {
    owner: string;
    attribution_window_days: number;
    budget_usd_per_run: number;
    success_event: string;
  };
  approvals: { tool: string; approved_at: string; approver: string }[];
  outcomes: Outcome[];
}
export interface Unmatched {
  event: Outcome;
  reason: 'no_run' | 'outside_window' | 'unknown_key_format';
}
