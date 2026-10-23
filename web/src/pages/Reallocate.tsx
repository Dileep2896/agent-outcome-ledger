import { ArrowRight, CalendarDays, ShieldCheck } from 'lucide-react';
import { money, useApi } from '../api';
import type { GateDecision, Plan } from '../types';
import { GateCard } from '../components/GateCard';
import { BudgetBars } from '../components/BudgetBars';
import { AnimatedNumber } from '../components/AnimatedNumber';
import { ErrorState, Loading, PageHeading } from '../components/States';
import { Reveal } from '../components/Reveal';
export function Reallocate() {
  const gates = useApi<GateDecision[]>('gate');
  const plan = useApi<Plan>('plan');
  if (gates.error) return <ErrorState message={gates.error} retry={gates.retry} />;
  if (plan.error) return <ErrorState message={plan.error} retry={plan.retry} />;
  if (!gates.data || !plan.data) return <Loading />;
  const replay = plan.data.replay;
  const lift = (replay.after_value / replay.before_value - 1) * 100;
  return (
    <main className="page reallocate-page">
      <div className="page-meta">
        <span className="small-label">Evidence before allocation</span>
        <span className="date-chip">
          <CalendarDays size={14} /> Plan for Oct 19–25
        </span>
      </div>
      <PageHeading
        title="Move budget. Not on a hunch."
        description="Keep the total spend. Change where the next dollar goes."
        link={{ href: '/ledger', label: 'Inspect the evidence' }}
      />
      <div className="gate-explainer">
        <ShieldCheck size={19} />
        <p>
          <strong>The promotion gate</strong> requires at least 30 challenger runs and a 90%
          advantage interval entirely above zero. An interval entirely below zero triggers rollback.
        </p>
      </div>
      <section className="gate-grid" aria-label="Promotion decisions">
        {gates.data.map((gate, i) => (
          <Reveal key={gate.workflow} delay={i * 0.08}>
            <GateCard gate={gate} />
          </Reveal>
        ))}
      </section>
      <div className="allocation-layout">
        <section className="allocation-panel">
          <div className="section-heading">
            <div>
              <h2>Next week’s budget</h2>
              <p>Conservative value per dollar, with room to keep learning.</p>
            </div>
          </div>
          <BudgetBars allocations={plan.data.allocations} total={replay.before_spend} />
          <div className="allocation-rules">
            <span>10% minimum share</span>
            <span>60% maximum share</span>
            <span className="mono">{money(replay.after_spend)} total</span>
          </div>
        </section>
        <section className="replay-panel">
          <span className="small-label">Replay last week</span>
          <h2>
            Same budget.
            <br />
            Different outcome.
          </h2>
          <p>
            Apply the proposed split to each selected variant’s observed value and cost per run.
          </p>
          <div className="replay-values">
            <div>
              <span>Observed value</span>
              <strong className="mono">{money(replay.before_value, 0)}</strong>
            </div>
            <ArrowRight size={22} />
            <div>
              <span>Projected value</span>
              <strong className="mono value">
                <AnimatedNumber value={replay.after_value} prefix="$" />
              </strong>
            </div>
          </div>
          <div className="replay-lift">
            <strong className="mono value">
              <AnimatedNumber value={lift} prefix="+" suffix="%" decimals={1} />
            </strong>
            <span>
              projected value
              <br />
              at the same {money(replay.after_spend)} spend
            </span>
          </div>
          <p className="fine-print">
            A replay on seed data, not a forecast. Assumes unchanged unit economics and enough
            eligible work; ignores capacity constraints and causal effects.
          </p>
        </section>
      </div>
      <div className="method-note">
        <h3>What the gate can tell you</h3>
        <p>
          Intervals describe the variation in this week’s runs. The extra-run estimate assumes the
          same effect and variance, with interval width shrinking as 1/√n. It is a planning aid, not
          a guarantee that more runs will clear the gate.
        </p>
      </div>
    </main>
  );
}
