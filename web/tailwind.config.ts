import type { Config } from 'tailwindcss';
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: 'var(--color-paper)',
        ink: 'var(--color-ink)',
        value: 'var(--color-accent)',
        spend: 'var(--color-negative)',
        muted: 'var(--color-muted)',
      },
    },
  },
  plugins: [],
} satisfies Config;
