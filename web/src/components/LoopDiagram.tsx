import { useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { AnimatedNumber } from './AnimatedNumber';
const nodes = [
  { x: 180, y: 65, label: 'Allocate', note: 'Set the contract' },
  { x: 450, y: 65, label: 'Work', note: 'Record each run' },
  { x: 720, y: 65, label: 'Outcome', note: 'Collect the result' },
  { x: 720, y: 255, label: 'Attribute', note: 'Normalize + window' },
  { x: 450, y: 255, label: 'Learn', note: 'Measure + gate' },
  { x: 180, y: 255, label: 'Reallocate', note: 'Move the budget' },
];
const paths = [
  'M260 65 H370',
  'M530 65 H640',
  'M800 65 Q870 65 870 160 Q870 255 800 255',
  'M640 255 H530',
  'M370 255 H260',
  'M100 255 Q30 255 30 160 Q30 65 100 65',
];
export function LoopDiagram({ naive, engine }: { naive: number; engine: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.4 });
  const reduced = useReducedMotion();
  const [mode, setMode] = useState<'before' | 'after' | null>(null);
  const after = mode ? mode === 'after' : Boolean(reduced || inView);
  return (
    <div className="loop-diagram" ref={ref}>
      <div className="loop-toolbar">
        <div className="segmented" aria-label="Attribution diagram state">
          <button aria-pressed={!after} onClick={() => setMode('before')}>
            Before
          </button>
          <button aria-pressed={after} onClick={() => setMode('after')}>
            After
          </button>
        </div>
        <span className="small muted">
          {after ? 'Connected by keys, windows, and evidence' : 'The learning loop is broken'}
        </span>
      </div>
      <svg
        viewBox="0 0 900 330"
        role="img"
        aria-label={`Allocate, work, outcome, attribute, learn, reallocate. ${after ? 'All connections complete.' : 'Attribution and learning connections are broken.'}`}
      >
        <defs>
          <marker
            id="flow-arrow"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>
        {paths.map((path, i) => (
          <g key={path}>
            <path d={path} className={`loop-path ${i >= 2 ? 'broken' : ''}`} fill="none" />
            {after && (
              <motion.path
                key={`active-${i}`}
                d={path}
                className="loop-path active-path"
                fill="none"
                markerEnd="url(#flow-arrow)"
                initial={{ pathLength: reduced ? 1 : 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: reduced ? 0.1 : 0.8,
                  delay: reduced ? 0 : i * 0.08,
                  ease: [0.22, 1, 0.36, 1],
                }}
              />
            )}
          </g>
        ))}
        {nodes.map((node, i) => (
          <g
            key={node.label}
            className={`loop-node ${after || i < 3 ? 'connected' : 'disconnected'}`}
          >
            <rect x={node.x - 80} y={node.y - 31} width="160" height="62" rx="5" />
            <text x={node.x} y={node.y + 5} textAnchor="middle" className="node-title">
              {node.label}
            </text>
            <text x={node.x} y={node.y + 55} textAnchor="middle" className="node-note">
              {node.note}
            </text>
          </g>
        ))}
      </svg>
      <ol className="loop-mobile" aria-label="Outcome loop stages">
        {nodes.map((node, i) => (
          <li key={node.label} className={after || i < 3 ? 'connected' : 'disconnected'}>
            <span className="mono">{i + 1}</span>
            <div>
              <strong>{node.label}</strong>
              <small>{node.note}</small>
            </div>
          </li>
        ))}
      </ol>
      <div className="loop-result">
        <span>Attribution coverage</span>
        <span className="mono muted">{(naive * 100).toFixed(1)}%</span>
        <ArrowRight size={18} />
        <strong className="mono value">
          <AnimatedNumber
            key={String(after)}
            from={naive * 100}
            value={(after ? engine : naive) * 100}
            decimals={1}
            suffix="%"
          />
        </strong>
      </div>
    </div>
  );
}
