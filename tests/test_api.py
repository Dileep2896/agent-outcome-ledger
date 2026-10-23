import sqlite3

import pytest
from fastapi.testclient import TestClient

from outcome_ledger.api import create_app
from outcome_ledger.seed import make_seed
from outcome_ledger.store import load_seed, read_seed


@pytest.fixture(scope="module")
def client():
    with TestClient(create_app(":memory:")) as client:
        yield client


def test_summary(client):
    response = client.get("/api/summary?week=2026-10-12")
    assert response.status_code == 200
    assert response.json()["totals"]["runs"] == 240
    assert len(response.json()["variants"]) == 6


@pytest.mark.parametrize("endpoint", ["runs", "unmatched", "gate", "plan", "impact"])
def test_endpoints(client, endpoint):
    assert client.get(f"/api/{endpoint}").status_code == 200


def test_run_filters_and_detail(client):
    rows = client.get("/api/runs?workflow=Refund%20triage&variant=challenger").json()
    assert len(rows) == 11
    detail = client.get(f"/api/runs/{rows[0]['id']}").json()
    assert detail["steps"]
    assert detail["contract"]["owner"]
    assert detail["cost_usd"] > 0


def test_flag_filter(client):
    rows = client.get("/api/runs?flag=missing_approval").json()
    assert len(rows) == 5


def test_unknown_run_is_404(client):
    assert client.get("/api/runs/not-found").status_code == 404


def test_invalid_week_is_rejected(client):
    assert client.get("/api/summary?week=not-a-date").status_code == 422
    assert client.get("/api/summary?week=2026-10-05").status_code == 404


def test_invalid_flag_is_rejected(client):
    assert client.get("/api/runs?flag=typo").status_code == 422


def test_unknown_api_never_returns_spa(client):
    assert client.get("/api/typo").status_code == 404


def test_root_redirects_to_story(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/story"


def test_sqlite_roundtrip_and_idempotent_seed():
    with sqlite3.connect(":memory:") as db:
        load_seed(db)
        load_seed(db)
        assert read_seed(db) == make_seed()
        assert db.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 240
        assert db.execute("SELECT COUNT(*) FROM credits").fetchone()[0] > 0
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"contracts", "runs", "steps", "outcomes", "credits"} <= tables
