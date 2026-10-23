import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .service import Ledger, build_ledger
from .store import load_seed, read_seed

ROOT = Path(__file__).resolve().parent.parent


def create_app(db_path: str = str(ROOT / ".cache/ledger.sqlite")) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path)
        try:
            with db:
                load_seed(db)
                app.state.ledger = build_ledger(read_seed(db))
        finally:
            db.close()
        yield

    app = FastAPI(title="Outcome Ledger", lifespan=lifespan, docs_url=None, redoc_url=None)

    def ledger(request: Request) -> Ledger:
        return request.app.state.ledger

    def row(data: Ledger, run):
        contract = next(c for c in data.data.contracts if c.id == run.contract_id)
        credits = [c for c in data.attribution.credits if c.run_id == run.id]
        return {
            **run.model_dump(),
            "workflow": contract.workflow,
            "flags": data.flags[run.id],
            "attributed_value": sum(c.value_usd for c in credits),
            "credits": credits,
        }

    @app.get("/api/summary")
    def summary(request: Request, week: date = date(2026, 10, 12)):
        if week != date(2026, 10, 12):
            raise HTTPException(404, "This demo contains the week of 2026-10-12 only.")
        return ledger(request).summary()

    @app.get("/api/runs")
    def runs(
        request: Request,
        workflow: str = "",
        variant: Literal["", "incumbent", "challenger"] = "",
        flag: Literal["", "over_budget", "missing_approval", "tool_not_allowed"] = "",
    ):
        data = ledger(request)
        rows = [
            row(data, run)
            for run in sorted(data.data.runs, key=lambda r: r.started_at, reverse=True)
        ]
        return [
            r
            for r in rows
            if (not workflow or r["workflow"] == workflow)
            and (not variant or r["variant"] == variant)
            and (not flag or any(f.code == flag for f in r["flags"]))
        ]

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str, request: Request):
        data = ledger(request)
        run = next((r for r in data.data.runs if r.id == run_id), None)
        if run is None:
            raise HTTPException(404, "Run not found")
        return {
            **row(data, run),
            "contract": next(c for c in data.data.contracts if c.id == run.contract_id),
            "outcomes": [
                e
                for e in data.data.events
                if e.id in {c.event_id for c in data.attribution.credits if c.run_id == run_id}
            ],
        }

    @app.get("/api/unmatched")
    def unmatched(request: Request):
        return ledger(request).attribution.unmatched

    @app.get("/api/gate")
    def gates(request: Request):
        return ledger(request).gates

    @app.get("/api/plan")
    def plan(request: Request):
        data = ledger(request)
        return {"allocations": data.plan, "replay": data.replay}

    @app.get("/api/impact")
    def impact(request: Request):
        return ledger(request).impact()

    @app.get("/")
    def root():
        return RedirectResponse("/story")

    dist = ROOT / "web/dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/favicon.svg", include_in_schema=False)
    def favicon():
        return FileResponse(ROOT / "web/public/favicon.svg")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path not in {"story", "ledger", "reallocate"}:
            raise HTTPException(404, "Page not found")
        if not (dist / "index.html").exists():
            raise HTTPException(503, "Build the frontend with pnpm --dir web build first.")
        return FileResponse(dist / "index.html")

    return app


app = create_app()
