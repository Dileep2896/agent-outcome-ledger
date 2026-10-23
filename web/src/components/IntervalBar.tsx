import { motion, useReducedMotion } from 'framer-motion';
import { number } from '../api';
export function IntervalBar({
  interval,
  point,
  verdict,
}: {
  interval: [number, number];
  point: number;
  verdict: string;
}) {
  const reduced = useReducedMotion();
  const extent = Math.max(Math.abs(interval[0]), Math.abs(interval[1]), Math.abs(point), 1) * 1.15;
  const pos = (value: number) => 50 + (value / extent) * 50;
  return (
    <div
      className={`interval ${verdict.toLowerCase()}`}
      role="img"
      aria-label={`90% interval from ${number(interval[0], 1)} to ${number(interval[1], 1)} dollars of value per dollar spent; zero is no advantage.`}
    >
      <div className="interval-axis" />
      <div className="interval-zero" />
      <motion.div
        className="interval-range"
        style={{ left: `${pos(interval[0])}%`, width: `${pos(interval[1]) - pos(interval[0])}%` }}
        initial={{ scaleX: reduced ? 1 : 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: reduced ? 0 : 0.8, ease: [0.22, 1, 0.36, 1] }}
      />
      <div className="interval-point" style={{ left: `${pos(point)}%` }} />
      <div className="interval-labels mono">
        <span>{number(-extent, 0)}</span>
        <span>0</span>
        <span>+{number(extent, 0)}</span>
      </div>
    </div>
  );
}
