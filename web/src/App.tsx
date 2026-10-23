import { MotionConfig } from 'framer-motion';
import { BookOpen, Code2, ArrowUpRight } from 'lucide-react';
import { Story } from './pages/Story';
import { Ledger } from './pages/Ledger';
import { Reallocate } from './pages/Reallocate';
export default function App() {
  const path = window.location.pathname;
  const current = path === '/' ? 'story' : path.replace('/', '');
  return (
    <MotionConfig reducedMotion="user">
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>
      <header className="site-header">
        <div className="nav-inner">
          <a className="wordmark" href="/story" aria-label="Outcome Ledger home">
            <span className="brand-symbol">
              <BookOpen size={20} strokeWidth={1.6} />
            </span>
            outcome<span className="wordmark-light">ledger</span>
          </a>
          <nav aria-label="Main navigation">
            {['story', 'ledger', 'reallocate'].map((page) => (
              <a key={page} href={`/${page}`} aria-current={current === page ? 'page' : undefined}>
                {page[0].toUpperCase() + page.slice(1)}
              </a>
            ))}
          </nav>
          <span className="nav-status">
            <span className="status-dot" /> Local demo <span className="nav-divider">/</span>{' '}
            <span className="mono">W42</span>
          </span>
        </div>
      </header>
      <div id="main-content">
        {current === 'ledger' ? (
          <Ledger />
        ) : current === 'reallocate' ? (
          <Reallocate />
        ) : current === 'story' ? (
          <Story />
        ) : (
          <main className="page state-panel">
            <h1>Page not found</h1>
            <a className="button primary" href="/story">
              Return to the story
            </a>
          </main>
        )}
      </div>
      <footer className="site-footer page">
        <a href="/story" className="footer-brand">
          <BookOpen size={17} /> Outcome Ledger
        </a>
        <p>Built with Codex. Made for evidence.</p>
        <a href="/openapi.json" className="footer-api">
          <Code2 size={15} /> API schema <ArrowUpRight size={14} />
        </a>
      </footer>
    </MotionConfig>
  );
}
