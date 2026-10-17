import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.main import app

SMALL_XML = b"""<testsuite tests="2">
  <testcase classname="tests.test_pricing" name="test_ok" time="0.001"/>
  <testcase classname="tests.test_pricing" name="test_bad" time="0.001">
    <failure message="assert 89.0 == 90.0">trace text</failure>
  </testcase>
</testsuite>"""

FORM = {"repo": "demo/shop", "branch": "main", "commit_sha": "abc123"}
HEADERS = {"X-API-Token": "test-token"}


@pytest.fixture
def client(monkeypatch):
    # an in memory sqlite database keeps these tests fast and separate from neon
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def override_db():
        with Session(engine) as db:
            yield db

    monkeypatch.setattr(settings, "ingest_token", "test-token")
    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def upload(client, xml=SMALL_XML, headers=HEADERS, **extra):
    return client.post(
        "/api/runs",
        files={"report": ("junit.xml", xml, "application/xml")},
        data={**FORM, **extra},
        headers=headers,
    )


def test_upload_stores_run_and_failures(client):
    response = upload(client)
    assert response.status_code == 201
    body = response.json()
    assert body["total_tests"] == 2
    assert body["failed_count"] == 1
    assert body["failures"][0]["error_type"] == "AssertionError"


def test_upload_without_token_is_rejected(client):
    assert upload(client, headers={}).status_code == 401


def test_upload_with_wrong_token_is_rejected(client):
    assert upload(client, headers={"X-API-Token": "nope"}).status_code == 401


def test_invalid_report_returns_422(client):
    assert upload(client, xml=b"not xml").status_code == 422


def test_list_runs_returns_newest_first(client):
    upload(client, pr_number="1")
    upload(client, pr_number="2")
    runs = client.get("/api/runs").json()
    assert [run["pr_number"] for run in runs] == [2, 1]


def test_get_run_returns_failures(client):
    run_id = upload(client).json()["id"]
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    assert len(response.json()["failures"]) == 1


def test_get_missing_run_returns_404(client):
    assert client.get("/api/runs/999").status_code == 404