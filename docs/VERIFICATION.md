# Verification record

Verified locally on 2026-10-22.

| Check | Result |
| --- | --- |
| `uv run pytest` | 85 passed |
| `uv run ruff check` | Passed |
| `pnpm --dir web test` | 5 passed |
| `pnpm --dir web build` | Strict TypeScript check and Vite production build passed |
| `make install` | Frozen Python and frontend dependency installation passed |
| CLI vs. API summary | Exact JSON equality |
| `GET /api/summary?week=2026-10-12` | HTTP 200 |
| `GET /story` | HTTP 200, served by FastAPI from the production build |
| Runtime external requests | None in the three-page browser check |

Core tests preceded their corresponding implementations. Additional regression tests cover expired reversals, the exact challenger sample threshold, and forward/backward keyboard focus in the run drawer.

The backend suite emits an upstream test-client deprecation notice for HTTPX. The frontend suite deliberately enables reduced motion and the animation library reports that setting. Both suites finish successfully.

Headless-browser checks covered Story, Ledger, and Reallocate at widths 320, 375, 414, 768, 1280, and 1920 pixels. No page overflow or JavaScript errors were observed. The approval filter, evidence drawer, Escape dismissal, and before/after diagram controls were exercised. Desktop and mobile screenshots accompany this record. A separate motion-enabled check verified that token, coverage, and impact counters reached the API values.

This is verification of the seeded local application, not validation of production integrations, causal inference, or projected business returns. No independent reviewer has certified the implementation.

## Independent verification (Claude Code)

Re-ran `uv run pytest` (85 passed after adding a gate test), `uv run ruff check`, `pnpm --dir web test` (5 passed) and `pnpm --dir web build`; reviewed the backend; browser-checked `/story`, `/ledger` and `/reallocate` on the production server. Fixes: the promotion gate now requires the minimum sample on both arms, and the startup SQLite handle is closed.
