import { ChevronDown } from 'lucide-react';
import type { Unmatched } from '../types';
import { money } from '../api';
const reasons = {
  no_run: 'No matching run',
  outside_window: 'Outside attribution window',
  unknown_key_format: 'Unknown key format',
};
export function UnmatchedPanel({ items }: { items: Unmatched[] }) {
  return (
    <details className="unmatched-panel">
      <summary>
        <div>
          <span className="small-label">Still unaccounted for</span>
          <h2>{items.length} outcomes need a closer look</h2>
        </div>
        <ChevronDown size={20} />
      </summary>
      <p className="muted">
        These outcomes stay visible in the denominator. Nothing disappears because it didn’t match.
      </p>
      <div className="unmatched-list">
        {items.map((item) => (
          <div className="unmatched-row" key={item.event.id}>
            <div>
              <span className="small-label">{item.event.source}</span>
              <code>{item.event.external_key}</code>
            </div>
            <span className="mono">
              {item.event.amount_usd === null ? 'Fixed value' : money(item.event.amount_usd)}
            </span>
            <span className="badge neutral">{reasons[item.reason]}</span>
          </div>
        ))}
      </div>
    </details>
  );
}
