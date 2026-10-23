import { motion, useReducedMotion } from 'framer-motion';
import { percent } from '../api';
export function CoverageBar({ naive, engine }: { naive: number; engine: number }) {
  const reduced = useReducedMotion();
  return (
    <div className="coverage-comparison">
      {[
        { label: 'Exact-ID join', value: naive, kind: 'naive' },
        { label: 'Outcome Ledger', value: engine, kind: 'engine' },
      ].map((item, i) => (
        <div className="coverage-row" key={item.kind}>
          <div className="coverage-label">
            <span>{item.label}</span>
            <strong className="mono">{percent(item.value)}</strong>
          </div>
          <div className="bar-track">
            <motion.div
              className={`bar-fill ${item.kind}`}
              style={{ width: `${item.value * 100}%`, transformOrigin: 'left' }}
              initial={{ scaleX: reduced ? 1 : 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{
                duration: reduced ? 0 : 0.8,
                delay: reduced ? 0 : i * 0.08,
                ease: [0.22, 1, 0.36, 1],
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
