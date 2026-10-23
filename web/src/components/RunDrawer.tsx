import { useEffect, useRef } from 'react';
import { X, Check, AlertTriangle } from 'lucide-react';
import { dateTime, money, number, useApi } from '../api';
import type { RunDetail } from '../types';
import { ErrorState, Loading } from './States';

export function RunDrawer({ id, onClose }: { id: string; onClose: () => void }) {
  const { data, error, retry } = useApi<RunDetail>(`runs/${id}`);
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const el = dialog.current;
    const before = document.activeElement as HTMLElement;
    if (el?.showModal) el.showModal();
    else el?.setAttribute('open', '');
    el?.querySelector<HTMLButtonElement>('button')?.focus();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = overflow;
      before?.focus();
    };
  }, []);
  return (
    <dialog
      ref={dialog}
      className="run-drawer"
      aria-labelledby="drawer-title"
      onKeyDown={(event) => {
        if (event.key !== 'Tab') return;
        const controls = Array.from(
          event.currentTarget.querySelectorAll<HTMLElement>(
            'button:not([disabled]), a[href], input:not([disabled]), ' +
              'select:not([disabled]), textarea:not([disabled]), [tabindex="0"]',
          ),
        ).filter((element) => !element.closest('[hidden]'));
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(event) => {
        if (event.target === dialog.current) {
          const rect = dialog.current.getBoundingClientRect();
          if (event.clientX < rect.left) onClose();
        }
      }}
    >
      <div className="drawer-heading">
        <div>
          <span className="small-label">Run evidence</span>
          <h2 id="drawer-title">{id}</h2>
        </div>
        <button className="icon-button" aria-label="Close run details" onClick={onClose}>
          <X size={22} />
        </button>
      </div>
      {error ? (
        <ErrorState message={error} retry={retry} />
      ) : !data ? (
        <Loading />
      ) : (
        <div className="drawer-body">
          <div className="drawer-context">
            <strong>{data.workflow}</strong>
            <span className="badge neutral">{data.variant}</span>
            <code>{data.entity_ref}</code>
            <span className="small muted">{dateTime(data.started_at)}</span>
          </div>
          <div className="drawer-metrics">
            <div>
              <span>Token spend</span>
              <strong className="mono">{money(data.cost_usd, 4)}</strong>
            </div>
            <div>
              <span>Attributed value</span>
              <strong className="mono value">{money(data.attributed_value)}</strong>
            </div>
          </div>
          <section>
            <h3>Work contract</h3>
            <dl className="contract-list">
              <div>
                <dt>Owner</dt>
                <dd>{data.contract.owner}</dd>
              </div>
              <div>
                <dt>Budget per run</dt>
                <dd className="mono">{money(data.contract.budget_usd_per_run)}</dd>
              </div>
              <div>
                <dt>Attribution window</dt>
                <dd>{data.contract.attribution_window_days} days</dd>
              </div>
            </dl>
          </section>
          <section>
            <h3>Steps & token costs</h3>
            <ol className="step-list">
              {data.steps.map((step, i) => (
                <li key={i}>
                  <span className="step-index mono">{String(i + 1).padStart(2, '0')}</span>
                  <div>
                    <code>{step.tool}</code>
                    <p className="small muted">
                      {step.model} · {number(step.input_tokens)} in / {number(step.output_tokens)}{' '}
                      out
                    </p>
                    <code className="step-args">{JSON.stringify(step.args)}</code>
                  </div>
                  <span className="mono small">{money(step.cost_usd, 4)}</span>
                </li>
              ))}
            </ol>
          </section>
          <section>
            <h3>Attribution trail</h3>
            {data.credits.length ? (
              data.credits.map((credit, i) => (
                <div className={`credit ${credit.value_usd < 0 ? 'reversal' : ''}`} key={i}>
                  <div className="credit-top">
                    <Check size={16} />
                    <strong className="mono">{money(credit.value_usd)}</strong>
                  </div>
                  <p>{credit.explanation}</p>
                  <code className="small">{credit.event_id}</code>
                </div>
              ))
            ) : (
              <p className="muted">No countable outcome credited to this run.</p>
            )}
          </section>
          <section>
            <h3>Governance checks</h3>
            {data.flags.length ? (
              data.flags.map((flag, i) => (
                <div className="flag-detail" key={i}>
                  <AlertTriangle size={17} />
                  <p>{flag.reason}</p>
                </div>
              ))
            ) : (
              <p className="pass-message">
                <Check size={16} /> All contract checks passed.
              </p>
            )}
            {data.approvals?.map((approval, i) => (
              <p className="small muted" key={i}>
                Approved by {approval.approver}: {approval.tool}, {dateTime(approval.approved_at)}
              </p>
            ))}
          </section>
        </div>
      )}
    </dialog>
  );
}
