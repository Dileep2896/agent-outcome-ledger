import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AnimatedNumber } from '../components/AnimatedNumber';
import { GateCard } from '../components/GateCard';
import { Story } from '../pages/Story';
import { Ledger } from '../pages/Ledger';
import type { GateDecision } from '../types';

const gate: GateDecision = {
  workflow: 'Refund triage',
  verdict: 'HOLD',
  reason: 'Only 11 runs; collect more evidence.',
  n_challenger: 11,
  n_incumbent: 69,
  difference_interval: [-20, 40],
  difference: 10,
  runs_needed: 19,
  chosen_variant: 'incumbent',
};
const impact = {
  naive_coverage: 0.35,
  engine_coverage: 0.98,
  before_value_per_dollar: 190,
  after_value_per_dollar: 570,
  flags_caught: 10,
  flagged_runs: 10,
  runs: 240,
  events: 195,
  spend: 94.26,
  tokens: 42000000,
  attributed_value: 18049,
  replay: { before_spend: 94.26, after_spend: 94.26, before_value: 18049, after_value: 54000 },
  gates: [gate],
  label: "Measured on the demo's seed data",
};

describe('Evidence UI', () => {
  it('shows the final animated number with reduced motion', () => {
    render(<AnimatedNumber value={98.8} suffix="%" decimals={1} />);
    expect(screen.getByText('98.8%')).toBeInTheDocument();
  });
  it('renders gate verdict, reason, and additional sample requirement', () => {
    render(<GateCard gate={gate} />);
    expect(screen.getByText('HOLD')).toBeInTheDocument();
    expect(screen.getByText(gate.reason)).toBeInTheDocument();
    expect(screen.getByText(/19 more runs/)).toBeInTheDocument();
  });
  it('renders all six story sections from measured API data', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(impact)));
    render(<Story />);
    expect(
      await screen.findByRole('heading', { name: /Your agents’ spend is itemized/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /The value arrives elsewhere/ }),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Close the loop/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /A cap controls spend/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Better is a claim/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Same spend. More evidence/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Open the ledger/ })).toHaveAttribute(
      'href',
      '/ledger',
    );
  });
  it('offers retry when the story API fails', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('Unavailable', { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(impact)));
    render(<Story />);
    await userEvent.click(await screen.findByRole('button', { name: 'Try again' }));
    expect(await screen.findByRole('heading', { name: /Your agents’ spend/ })).toBeInTheDocument();
  });
  it('filters ledger runs and opens a detail drawer', async () => {
    const metrics = {
      runs: 1,
      spend: 1,
      attributed_value: 20,
      successes: 1,
      success_rate: 1,
      value_per_dollar: 20,
      cost_per_success: 1,
      interval: [10, 30],
    };
    const run = {
      id: 'refund-i-001',
      workflow: 'Refund triage',
      variant: 'incumbent',
      entity_ref: 'ticket:1',
      started_at: '2026-10-12T10:00:00Z',
      cost_usd: 1,
      attributed_value: 20,
      flags: [],
      steps: [],
      credits: [],
    };
    const summary = {
      week: '2026-10-12',
      totals: metrics,
      coverage: {
        naive: 0.35,
        engine: 0.98,
        total_outcome_value: 20,
        naive_value: 7,
        unmatched_count: 0,
      },
      workflows: [{ workflow: 'Refund triage', ...metrics }],
      variants: [{ workflow: 'Refund triage', variant: 'incumbent', ...metrics }],
    };
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      const body = url.includes('/summary')
        ? summary
        : url.includes('/unmatched')
          ? []
          : url.includes('/runs/refund')
            ? {
                ...run,
                contract: { owner: 'Mara Vale', budget_usd_per_run: 2, attribution_window_days: 7 },
                outcomes: [],
              }
            : url.includes('flag=missing_approval')
              ? []
              : [run];
      return new Response(JSON.stringify(body));
    });
    render(<Ledger />);
    await userEvent.click(await screen.findByRole('button', { name: /refund-i-001/ }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    const close = screen.getByRole('button', { name: 'Close run details' });
    close.focus();
    await userEvent.tab();
    expect(close).toHaveFocus();
    await userEvent.tab({ shift: true });
    expect(close).toHaveFocus();
    await userEvent.click(close);
    await userEvent.selectOptions(screen.getByLabelText('Governance flag'), 'missing_approval');
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('flag=missing_approval'),
        expect.anything(),
      ),
    );
    expect(await screen.findByText('No runs match these filters.')).toBeInTheDocument();
  });
});
