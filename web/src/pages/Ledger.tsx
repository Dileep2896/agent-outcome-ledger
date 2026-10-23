import { useState } from 'react';
import { ArrowUpRight, CalendarDays, Filter, X } from 'lucide-react';
import { money, number, useApi } from '../api';
import type { Run, Summary, Unmatched, Variant } from '../types';
import { AnimatedNumber } from '../components/AnimatedNumber';
import { CoverageBar } from '../components/CoverageBar';
import { WorkflowTable } from '../components/WorkflowTable';
import { UnmatchedPanel } from '../components/UnmatchedPanel';
import { RunDrawer } from '../components/RunDrawer';
import { ErrorState, Loading, PageHeading } from '../components/States';

export function Ledger() {
  const summary = useApi<Summary>('summary?week=2026-10-12');
  const unmatched = useApi<Unmatched[]>('unmatched');
  const [filters, setFilters] = useState({ workflow: '', variant: '', flag: '' });
  const runs = useApi<Run[]>(`runs?${new URLSearchParams(filters)}`);
  const [selected, setSelected] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const setFilter = (key: string, value: string) => {
    setPage(0);
    setFilters((f) => ({ ...f, [key]: value }));
  };
  const selectVariant = (workflow: string, variant: Variant) => {
    setPage(0);
    setFilters((f) => ({ ...f, workflow, variant }));
    document
      .getElementById('run-evidence')
      ?.scrollIntoView({
        block: 'start',
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      });
  };
  if (summary.error) return <ErrorState message={summary.error} retry={summary.retry} />;
  if (!summary.data) return <Loading />;
  const data = summary.data;
  const displayed = runs.data?.slice(page * 12, (page + 1) * 12) ?? [];
  return (
    <main className="page ledger-page">
      <div className="page-meta">
        <span className="small-label">Weekly outcome review</span>
        <span className="date-chip">
          <CalendarDays size={14} /> Oct 12–18, 2026
        </span>
      </div>
      <PageHeading
        title="Every dollar. An outcome."
        description="Follow your agents’ spend through to the work it produced."
        link={{ href: '/reallocate', label: 'Review allocation' }}
      />
      <section className="metric-grid" aria-label="Weekly summary">
        <div className="metric-cell">
          <span>Token spend</span>
          <strong className="mono">
            <AnimatedNumber value={data.totals.spend} prefix="$" decimals={2} />
          </strong>
          <small>{data.totals.runs} agent runs · 3 workflows</small>
        </div>
        <div className="metric-cell">
          <span>Attributed value</span>
          <strong className="mono value">
            <AnimatedNumber value={data.totals.attributed_value} prefix="$" />
          </strong>
          <small>Net of reversed outcomes</small>
        </div>
        <div className="metric-cell">
          <span>Value per $1 of tokens</span>
          <strong className="mono">
            <AnimatedNumber value={data.totals.value_per_dollar} decimals={1} suffix="×" />
          </strong>
          <small>Observed value / token cost</small>
        </div>
        <div className="metric-cell">
          <span>Attribution coverage</span>
          <strong className="mono value">
            <AnimatedNumber value={data.coverage.engine * 100} decimals={1} suffix="%" />
          </strong>
          <small>{data.coverage.unmatched_count} unmatched outcomes remain</small>
        </div>
      </section>
      <section className="coverage-panel">
        <div>
          <h2>The same outcomes. A better join.</h2>
          <p>Normalize the keys. Respect the window. Recover the connection.</p>
          <span className="small muted">
            Coverage is the share of net outcome value attributed to runs.
          </span>
        </div>
        <CoverageBar naive={data.coverage.naive} engine={data.coverage.engine} />
      </section>
      <section className="workflow-section">
        <div className="section-heading">
          <div>
            <h2>Workflow economics</h2>
            <p>
              Click a variant to inspect its runs. Intervals use 2,000 seeded bootstrap resamples.
            </p>
          </div>
          <span className="small mono">6 variants / 3 workflows</span>
        </div>
        <WorkflowTable rows={data.variants} onSelect={selectVariant} selected={filters} />
      </section>
      <section id="run-evidence" className="runs-section">
        <div className="section-heading">
          <div>
            <h2>
              Run evidence <span className="count">{runs.data?.length ?? '—'}</span>
            </h2>
            <p>Open a run to see the steps, credit trail, and contract checks.</p>
          </div>
        </div>
        <div className="filter-bar">
          <Filter size={16} />
          <label>
            <span className="sr-only">Workflow</span>
            <select
              value={filters.workflow}
              onChange={(e) => setFilter('workflow', e.target.value)}
            >
              <option value="">All workflows</option>
              {data.workflows.map((w) => (
                <option key={w.workflow}>{w.workflow}</option>
              ))}
            </select>
          </label>
          <label>
            <span className="sr-only">Variant</span>
            <select value={filters.variant} onChange={(e) => setFilter('variant', e.target.value)}>
              <option value="">All variants</option>
              <option value="incumbent">Incumbent</option>
              <option value="challenger">Challenger</option>
            </select>
          </label>
          <label>
            <span className="sr-only">Governance flag</span>
            <select value={filters.flag} onChange={(e) => setFilter('flag', e.target.value)}>
              <option value="">All contract checks</option>
              <option value="missing_approval">Missing approval</option>
              <option value="over_budget">Over budget</option>
              <option value="tool_not_allowed">Tool not allowed</option>
            </select>
          </label>
          {Object.values(filters).some(Boolean) && (
            <button
              className="text-button"
              onClick={() => {
                setFilters({ workflow: '', variant: '', flag: '' });
                setPage(0);
              }}
            >
              <X size={14} />
              Clear
            </button>
          )}
        </div>
        {runs.error ? (
          <ErrorState message={runs.error} retry={runs.retry} />
        ) : runs.loading ? (
          <Loading />
        ) : !displayed.length ? (
          <div className="empty-state">No runs match these filters.</div>
        ) : (
          <>
            <div className="run-grid">
              {displayed.map((run) => (
                <button key={run.id} className="run-card" onClick={() => setSelected(run.id)}>
                  <div className="run-top">
                    <code>{run.id}</code>
                    <ArrowUpRight size={16} />
                  </div>
                  <strong>{run.workflow}</strong>
                  <span className="entity-ref mono">{run.entity_ref}</span>
                  <div className="run-economics">
                    <span>{money(run.cost_usd)} spent</span>
                    <span className="value">{money(run.attributed_value, 0)} value</span>
                  </div>
                  <div className="run-foot">
                    <span>{run.variant}</span>
                    <span className={run.flags.length ? 'flag-label' : 'muted'}>
                      {run.flags.length
                        ? `${run.flags.length} flag${run.flags.length > 1 ? 's' : ''}`
                        : 'Checks passed'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
            <div className="pagination">
              <span className="small muted">
                Showing {page * 12 + 1}–{Math.min((page + 1) * 12, runs.data?.length ?? 0)} of{' '}
                {number(runs.data?.length ?? 0)} runs
              </span>
              <div>
                <button
                  className="button secondary"
                  disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </button>
                <button
                  className="button secondary"
                  disabled={(page + 1) * 12 >= (runs.data?.length ?? 0)}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </section>
      {unmatched.error ? (
        <ErrorState message={unmatched.error} retry={unmatched.retry} />
      ) : unmatched.data ? (
        <UnmatchedPanel items={unmatched.data} />
      ) : (
        <Loading label="Loading unmatched outcomes…" />
      )}
      {selected && <RunDrawer id={selected} onClose={() => setSelected(null)} />}
    </main>
  );
}
