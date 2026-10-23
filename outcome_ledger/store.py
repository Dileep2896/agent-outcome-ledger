"""SQLite audit ledger. Costs are recomputed from tokens on deserialization."""

import json
import sqlite3

from .attribution import attribute
from .models import AgentRun, OutcomeEvent, SeedData, WorkContract
from .seed import NOW, WEEK, make_seed
from .sources import MockBilling, MockCRM, MockHelpdesk

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS contracts (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY, contract_id TEXT REFERENCES contracts(id), payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS steps (
    run_id TEXT REFERENCES runs(id), ordinal INTEGER, payload TEXT NOT NULL,
    PRIMARY KEY (run_id, ordinal));
CREATE TABLE IF NOT EXISTS outcomes (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS credits (
    run_id TEXT REFERENCES runs(id), event_id TEXT REFERENCES outcomes(id), value_usd REAL,
    explanation TEXT, PRIMARY KEY (run_id, event_id));
"""


def load_seed(db: sqlite3.Connection) -> None:
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]:
        return
    data = make_seed()
    sources = [MockCRM(data.events), MockBilling(data.events), MockHelpdesk(data.events)]
    events = [event for source in sources for event in source.fetch(WEEK, NOW)]
    result = attribute(data.contracts, data.runs, events)
    with db:
        db.executemany(
            "INSERT INTO contracts VALUES (?, ?)",
            [(c.id, c.model_dump_json()) for c in data.contracts],
        )
        for run in data.runs:
            payload = run.model_dump(mode="json", exclude={"cost_usd", "steps"})
            db.execute(
                "INSERT INTO runs VALUES (?, ?, ?)", (run.id, run.contract_id, json.dumps(payload))
            )
            db.executemany(
                "INSERT INTO steps VALUES (?, ?, ?)",
                [
                    (run.id, i, step.model_dump_json(exclude={"cost_usd"}))
                    for i, step in enumerate(run.steps)
                ],
            )
        db.executemany(
            "INSERT INTO outcomes VALUES (?, ?)",
            [(event.id, event.model_dump_json()) for event in events],
        )
        db.executemany(
            "INSERT INTO credits VALUES (?, ?, ?, ?)",
            [(c.run_id, c.event_id, c.value_usd, c.explanation) for c in result.credits],
        )


def read_seed(db: sqlite3.Connection) -> SeedData:
    contracts = [
        WorkContract.model_validate_json(row[0])
        for row in db.execute("SELECT payload FROM contracts ORDER BY rowid")
    ]
    runs = []
    for run_id, payload in db.execute("SELECT id, payload FROM runs ORDER BY rowid"):
        values = json.loads(payload)
        values["steps"] = [
            json.loads(row[0])
            for row in db.execute(
                "SELECT payload FROM steps WHERE run_id=? ORDER BY ordinal", (run_id,)
            )
        ]
        runs.append(AgentRun.model_validate(values))
    events = [
        OutcomeEvent.model_validate_json(row[0])
        for row in db.execute("SELECT payload FROM outcomes")
    ]
    # Preserve the deterministic generator's event order for a lossless round trip.
    order = {e.id: i for i, e in enumerate(make_seed().events)}
    events.sort(key=lambda event: order.get(event.id, len(order)))
    return SeedData(contracts=contracts, runs=runs, events=events, as_of=NOW)
