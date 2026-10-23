import { motion, useReducedMotion } from 'framer-motion';
import {
  ArrowDown,
  ArrowRight,
  Check,
  Database,
  FileText,
  GitMerge,
  Layers3,
  Shield,
  Ticket,
  Unplug,
} from 'lucide-react';
import { number, percent, useApi } from '../api';
import type { Impact } from '../types';
import { AnimatedNumber } from '../components/AnimatedNumber';
import { GateCard } from '../components/GateCard';
import { LoopDiagram } from '../components/LoopDiagram';
import { Reveal } from '../components/Reveal';
import { ErrorState, Loading } from '../components/States';

export function Story() {
  const { data, error, retry } = useApi<Impact>('impact');
  const reduced = useReducedMotion();
  if (error) return <ErrorState message={error} retry={retry} />;
  if (!data) return <Loading label="Following the money…" />;
  const sources = [
    {
      name: 'CRM',
      key: 'Dana.Lee+promo@Example.com',
      agent: 'lead:dana.lee@example.com',
      Icon: Database,
      note: 'A lead qualifies',
    },
    {
      name: 'Billing',
      key: 'INV-2026-00417',
      agent: 'invoice:417',
      Icon: FileText,
      note: 'An invoice is paid',
    },
    {
      name: 'Helpdesk',
      key: 'HS-10293',
      agent: 'ticket:10293',
      Icon: Ticket,
      note: 'A refund is resolved',
    },
  ];
  return (
    <main className="story-page">
      <section className="story-hero page">
        <div className="hero-copy">
          <Reveal>
            <div className="hero-label">
              <span className="status-dot" /> An open ledger for agent outcomes
            </div>
            <h1>
              Your agents’ spend
              <br className="desktop-break" /> is itemized.
              <br />
              <span>What it produced isn’t.</span>
            </h1>
            <p className="hero-lede">
              The cost shows up in your logs.
              <br />
              The value shows up somewhere else.
              <br />
              It’s time to connect the two.
            </p>
            <a className="button primary" href="/ledger">
              Explore the ledger <ArrowRight size={17} />
            </a>
            <span className="hero-footnote">
              A working demo. Real calculations. Fictional data.
            </span>
          </Reveal>
        </div>
        <Reveal className="hero-proof" delay={0.16}>
          <div className="receipt">
            <div className="receipt-header">
              <Layers3 size={20} />
              <span>Weekly agent activity</span>
              <span className="mono small">W42</span>
            </div>
            <div className="receipt-line">
              <span>Tokens consumed</span>
              <strong className="mono">
                <AnimatedNumber value={data.tokens} />
              </strong>
            </div>
            <div className="receipt-total">
              <span>Spend, accounted for.</span>
              <strong className="mono">
                <AnimatedNumber value={data.spend} prefix="$" decimals={2} />
              </strong>
            </div>
            <div className="receipt-rule">
              <span />
              <Unplug size={20} />
              <span />
            </div>
            <div className="receipt-unknown">
              <span>Value, unaccounted for.</span>
              <strong className="mono">?</strong>
              <small>The answer isn’t in the token log.</small>
            </div>
            <div className="receipt-footer">
              <span>{data.runs} runs</span>
              <span>3 workflows</span>
              <span>{data.events} outcomes</span>
            </div>
          </div>
          <div className="receipt-annotation">
            <span className="annotation-line" /> Every cost has a record.
            <br />
            Every outcome should, too.
          </div>
        </Reveal>
        <div className="hero-bottom">
          <a href="#the-gap">
            Follow the outcome <ArrowDown size={15} />
          </a>
          <span className="mono">Oct 12–18, 2026 / seed snapshot</span>
        </div>
      </section>
      <section id="the-gap" className="story-section pain-section">
        <div className="page">
          <Reveal>
            <h2>
              The value arrives elsewhere.
              <br />
              <span className="muted">Under a different name.</span>
            </h2>
            <p className="section-lede">
              An agent finishes its run. Days later, the result lands in another system.
              <br className="desktop-break" /> The work is connected. The identifiers aren’t.
            </p>
          </Reveal>
          <div className="source-grid">
            {sources.map(({ name, key, agent, Icon, note }, i) => (
              <Reveal key={name} delay={i * 0.08}>
                <div className="source-card">
                  <div className="source-heading">
                    <Icon size={18} />
                    <span>{name}</span>
                    <span className="small muted">+2.1 days</span>
                  </div>
                  <h3>{note}</h3>
                  <code>{key}</code>
                </div>
                <div className="broken-connector">
                  <span />
                  <Unplug size={17} />
                  <span />
                </div>
                <div className="agent-key">
                  <span className="small muted">Agent’s entity key</span>
                  <code>{agent}</code>
                </div>
              </Reveal>
            ))}
          </div>
          <Reveal className="pain-caption">
            <strong className="mono">
              <AnimatedNumber value={data.naive_coverage * 100} decimals={1} suffix="%" />
            </strong>
            <p>
              of net outcome value connects with an exact-ID join.
              <br />
              <span className="muted">The rest looks like spend without a result.</span>
            </p>
          </Reveal>
        </div>
      </section>
      <section className="story-section loop-section page">
        <Reveal>
          <h2>
            Close the loop.
            <br />
            <span className="value">Then let the evidence travel.</span>
          </h2>
          <p className="section-lede">
            Normalize each system’s keys. Match inside the contract’s time window.
            <br className="desktop-break" /> Carry the explanation all the way to the next budget
            decision.
          </p>
        </Reveal>
        <Reveal>
          <LoopDiagram naive={data.naive_coverage} engine={data.engine_coverage} />
        </Reveal>
        <div className="loop-notes">
          <span>
            <Check size={15} /> Equal credit when runs share an outcome
          </span>
          <span>
            <Check size={15} /> Reversals remove prior credit
          </span>
          <span>
            <Check size={15} /> Unmatched events stay visible
          </span>
        </div>
      </section>
      <section className="story-section decision-section">
        <div className="page decision-layout">
          <Reveal>
            <h2>
              A cap controls spend.
              <br />A ledger explains it.
            </h2>
            <p className="section-lede">
              The useful question isn’t only “Did the agent stay within budget?” It’s “Did that
              budget produce something worth repeating?”
            </p>
          </Reveal>
          <div className="decision-options">
            <Reveal className="guard-option">
              <Shield size={21} />
              <div>
                <h3>Budget guard</h3>
                <p>Caps + approvals</p>
                <span>Gateways already do caps; they don’t say what spend produced.</span>
              </div>
            </Reveal>
            <Reveal className="ledger-option" delay={0.08}>
              <GitMerge size={22} />
              <div>
                <h3>Outcome Ledger</h3>
                <p>Spend → result → next decision</p>
                <ul>
                  {[
                    'Trace a result back to the work that earned it.',
                    'Separate repeatable advantage from a lucky run.',
                    'Give the next dollar a reason to go somewhere.',
                  ].map((reason, i) => (
                    <motion.li
                      key={reason}
                      initial={{ opacity: 0, y: reduced ? 0 : 8 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{
                        duration: reduced ? 0.1 : 0.5,
                        delay: reduced ? 0 : i * 0.08,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                    >
                      <Check size={15} />
                      {reason}
                    </motion.li>
                  ))}
                </ul>
              </div>
            </Reveal>
          </div>
        </div>
      </section>
      <section className="story-section page story-gates">
        <Reveal>
          <div className="story-gate-heading">
            <div>
              <h2>
                Better is a claim.
                <br />
                <span className="value">Promotion takes evidence.</span>
              </h2>
              <p className="section-lede">
                A challenger can look ~2× better on 11 runs and still be noise.
                <br className="desktop-break" /> The gate waits until the advantage clears zero and
                the sample is large enough.
              </p>
            </div>
            <div className="confidence-label">
              <span className="mono">90%</span>
              <span>
                bootstrap interval
                <br />
                30-run challenger minimum
              </span>
            </div>
          </div>
        </Reveal>
        <div className="gate-grid">
          {data.gates.map((gate, i) => (
            <Reveal key={gate.workflow} delay={i * 0.08}>
              <GateCard gate={gate} />
            </Reveal>
          ))}
        </div>
        <p className="fine-print">
          Intervals show the challenger’s change in value per $1 of tokens. Zero means no advantage.
          Additional-run estimates assume the same effect and variance.
        </p>
      </section>
      <section className="story-section impact-section">
        <div className="page">
          <Reveal>
            <div className="impact-heading">
              <h2>
                Same spend.
                <br />
                More evidence.
              </h2>
              <span className="seed-label">{data.label}</span>
            </div>
          </Reveal>
          <div className="impact-grid">
            <Reveal>
              <div className="impact-metric">
                <span>Outcome value connected</span>
                <div className="impact-before mono">
                  {percent(data.naive_coverage)} <ArrowRight size={20} />
                </div>
                <strong className="mono">
                  <AnimatedNumber
                    value={data.engine_coverage * 100}
                    from={data.naive_coverage * 100}
                    decimals={1}
                    suffix="%"
                  />
                </strong>
                <small>Exact-ID join → normalized attribution</small>
              </div>
            </Reveal>
            <Reveal delay={0.08}>
              <div className="impact-metric">
                <span>Value per $1 of tokens</span>
                <div className="impact-before mono">
                  {number(data.before_value_per_dollar, 1)}× <ArrowRight size={20} />
                </div>
                <strong className="mono">
                  <AnimatedNumber value={data.after_value_per_dollar} decimals={1} suffix="×" />
                </strong>
                <small>Observed → replayed at the same spend</small>
              </div>
            </Reveal>
            <Reveal delay={0.16}>
              <div className="impact-metric">
                <span>Governance flags caught</span>
                <div className="impact-before">Across {data.flagged_runs} runs</div>
                <strong className="mono">
                  <AnimatedNumber value={data.flags_caught} />
                </strong>
                <small>Overruns, missing approvals, disallowed tools</small>
              </div>
            </Reveal>
          </div>
          <Reveal className="impact-cta">
            <div>
              <h3>The evidence is open.</h3>
              <p>Inspect the runs. Follow the credit. Challenge the allocation.</p>
            </div>
            <a className="button light" href="/ledger">
              Open the ledger <ArrowRight size={18} />
            </a>
          </Reveal>
          <p className="impact-disclaimer">
            Seed data only. Replay assumes unchanged unit economics and available work. Attribution
            is not causal inference.
          </p>
        </div>
      </section>
    </main>
  );
}
