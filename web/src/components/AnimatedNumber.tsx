import { animate, useInView, useReducedMotion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { number } from '../api';

export function AnimatedNumber({
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
  from = 0,
}: {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  from?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const visible = useInView(ref, { once: true });
  const reduced = useReducedMotion();
  const [current, setCurrent] = useState(from);
  useEffect(() => {
    if (reduced) {
      setCurrent(value);
      return;
    }
    if (!visible) return;
    const controls = animate(from, value, {
      duration: 1.25,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: setCurrent,
    });
    return () => controls.stop();
  }, [value, visible, reduced, from]);
  return (
    <span
      ref={ref}
      className="tabular-nums"
      aria-label={`${prefix}${number(value, decimals)}${suffix}`}
    >
      <span aria-hidden="true">
        {prefix}
        {number(current, decimals)}
        {suffix}
      </span>
    </span>
  );
}
