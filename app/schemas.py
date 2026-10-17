from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FailureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_name: str
    classname: str
    error_type: str
    message: str
    stack_trace: str
    duration: float


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repo: str
    branch: str
    commit_sha: str
    pr_number: int | None
    total_tests: int
    failed_count: int
    created_at: datetime


class RunDetail(RunOut):
    failures: list[FailureOut]