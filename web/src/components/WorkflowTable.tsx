import { ArrowUpRight } from 'lucide-react';
import { money, number, percent } from '../api';
import type { Variant, VariantMetrics } from '../types';
export function WorkflowTable({
  rows,
  onSelect,
  selected,
}: {
  rows: VariantMetrics[];
  onSelect: (workflow: string, variant: Variant) => void;
  selected: { workflow: string; variant: string };
}) {
  return (
    <div className="table-wrap">
      <table className="workflow-table">
        <thead>
          <tr>
            <th>Workflow / variant</th>
            <th>Runs</th>
            <th>Token spend</th>
            <th>Attributed value</th>
            <th>Value / $1</th>
            <th>Success rate</th>
            <th>Cost / success</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.workflow + row.variant}
              className={
                selected.workflow === row.workflow && selected.variant === row.variant
                  ? 'selected'
                  : ''
              }
            >
              <td>
                <button
                  onClick={() => onSelect(row.workflow, row.variant)}
                  className="workflow-link"
                >
                  <span>
                    {row.workflow}
                    <span className={`variant-label ${row.variant}`}>
                      {row.variant === 'incumbent' ? 'v1 · incumbent' : 'v2 · challenger'}
                    </span>
                  </span>
                  <ArrowUpRight size={15} />
                </button>
              </td>
              <td data-label="Runs" className="mono">
                {row.runs}
              </td>
              <td data-label="Token spend" className="mono">
                {money(row.spend)}
              </td>
              <td data-label="Attributed value" className="mono value">
                {money(row.attributed_value, 0)}
              </td>
              <td data-label="Value / $1" className="mono">
                <strong>{number(row.value_per_dollar, 1)}×</strong>
                <span className="table-sub">
                  {number(row.interval[0], 0)}–{number(row.interval[1], 0)} · 90% CI
                </span>
              </td>
              <td data-label="Success rate" className="mono">
                {percent(row.success_rate)}
              </td>
              <td data-label="Cost / success" className="mono">
                {row.cost_per_success === null ? '—' : money(row.cost_per_success)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
