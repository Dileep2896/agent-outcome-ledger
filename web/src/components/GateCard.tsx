import { ArrowDownRight, ArrowUpRight, Pause } from 'lucide-react';
import type { GateDecision } from '../types';
import { IntervalBar } from './IntervalBar';
const icons = { PROMOTE: ArrowUpRight, HOLD: Pause, ROLLBACK: ArrowDownRight };
export function GateCard({ gate }: { gate: GateDecision }) {
  const Icon = icons[gate.verdict];
  return (
    <article className={`gate-card ${gate.verdict.toLowerCase()}`}>
      <div className="gate-top">
        <span className={`badge ${gate.verdict.toLowerCase()}`}>
          <Icon size={13} />
          {gate.verdict}
        </span>
        <span className="small mono">n = {gate.n_challenger}</span>
      </div>
      <h3>{gate.workflow}</h3>
      <p className="small muted">Challenger vs. incumbent · 90% interval</p>
      <IntervalBar
        interval={gate.difference_interval}
        point={gate.difference}
        verdict={gate.verdict}
      />
      <p className="gate-reason">{gate.reason}</p>
      <div className="gate-footer">
        {gate.verdict === 'HOLD' ? (
          <>
            <span className="mono">~{gate.runs_needed} more runs</span>
            <span>Keep incumbent</span>
          </>
        ) : (
          <>
            <span>Next week’s variant</span>
            <strong>{gate.chosen_variant}</strong>
          </>
        )}
      </div>
    </article>
  );
}
