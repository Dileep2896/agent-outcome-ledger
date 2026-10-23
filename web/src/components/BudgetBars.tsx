import { motion, useReducedMotion } from 'framer-motion';
import type { Allocation } from '../types';
import { money, percent } from '../api';
export function BudgetBars({ allocations, total }: { allocations: Allocation[]; total: number }) {
  const reduced = useReducedMotion();
  return (
    <div className="budget-bars">
      {allocations.map((row) => (
        <div className="budget-row" key={row.workflow}>
          <div className="budget-row-head">
            <strong>{row.workflow}</strong>
            <span className="small muted">Route to {row.variant}</span>
          </div>
          <div className="budget-line">
            <span className="small muted">Before</span>
            <div className="bar-track">
              <div
                className="bar-fill naive"
                style={{ width: `${(row.before_budget / total) * 100}%` }}
              />
            </div>
            <span className="mono small">{money(row.before_budget)}</span>
          </div>
          <div className="budget-line">
            <span className="small">After</span>
            <div className="bar-track">
              <motion.div
                className="bar-fill engine"
                style={{ width: `${row.share * 100}%`, transformOrigin: 'left' }}
                initial={{ scaleX: reduced ? 1 : 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: reduced ? 0 : 0.9, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
            <span className="mono small value">{money(row.budget)}</span>
          </div>
          <div className="budget-share mono small">{percent(row.share)} of next week’s budget</div>
        </div>
      ))}
    </div>
  );
}
