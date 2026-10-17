import secrets
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, get_db, get_engine
from app.models import Failure, Run
from app.parser import parse_junit
from app.schemas import RunDetail, RunOut

# reports are small text files so five megabytes is a generous limit
MAX_REPORT_BYTES = 5 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    # creates the tables on first start so no manual migration is needed yet
    Base.metadata.create_all(get_engine())
    yield


app = FastAPI(title="QA Intel Platform", lifespan=lifespan)


def require_token(x_api_token: str = Header(default="")) -> None:
    # an empty server token means ingest is disabled
    expected = settings.ingest_token
    if not expected or not secrets.compare_digest(x_api_token.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="invalid or missing api token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/runs", response_model=RunDetail, status_code=201, dependencies=[Depends(require_token)])
async def create_run(
    report: UploadFile = File(...),
    repo: str = Form(...),
    branch: str = Form(...),
    commit_sha: str = Form(...),
    pr_number: int | None = Form(None),
    db: Session = Depends(get_db),
):
    data = await report.read(MAX_REPORT_BYTES + 1)
    if len(data) > MAX_REPORT_BYTES:
        raise HTTPException(status_code=413, detail="report is larger than five megabytes")
    try:
        parsed = parse_junit(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    run = Run(
        repo=repo,
        branch=branch,
        commit_sha=commit_sha,
        pr_number=pr_number,
        total_tests=parsed.total_tests,
        failed_count=len(parsed.failures),
    )
    run.failures = [Failure(**asdict(item)) for item in parsed.failures]
    db.add(run)
    db.commit()
    db.refresh(run)
    # validate while the session is still open so lazy loaded failures are available
    return RunDetail.model_validate(run)


@app.get("/api/runs", response_model=list[RunOut])
def list_runs(limit: int = 50, db: Session = Depends(get_db)):
    query = select(Run).order_by(Run.id.desc()).limit(min(max(limit, 1), 200))
    return db.scalars(query).all()


@app.get("/api/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunDetail.model_validate(run)