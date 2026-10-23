import { ArrowRight, RotateCcw } from 'lucide-react';
export function Loading({ label = 'Loading the evidence…' }: { label?: string }) {
  return (
    <div className="state-panel" role="status">
      <span className="loading-line" />
      {label}
    </div>
  );
}
export function ErrorState({ message, retry }: { message: string; retry: () => void }) {
  return (
    <div className="state-panel error-state" role="alert">
      <h2>The evidence couldn’t load.</h2>
      <p>{message}</p>
      <button className="button secondary" onClick={retry}>
        <RotateCcw size={16} />
        Try again
      </button>
    </div>
  );
}
export function PageHeading({
  title,
  description,
  link,
}: {
  title: string;
  description: string;
  link?: { href: string; label: string };
}) {
  return (
    <div className="page-heading">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {link && (
        <a className="button secondary" href={link.href}>
          {link.label}
          <ArrowRight size={16} />
        </a>
      )}
    </div>
  );
}
