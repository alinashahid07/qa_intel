from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    repo: Mapped[str] = mapped_column(String(200))
    branch: Mapped[str] = mapped_column(String(200))
    commit_sha: Mapped[str] = mapped_column(String(64))
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    failures: Mapped[list["Failure"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class Failure(Base):
    __tablename__ = "failures"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    test_name: Mapped[str] = mapped_column(String(300))
    classname: Mapped[str] = mapped_column(String(300))
    error_type: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    stack_trace: Mapped[str] = mapped_column(Text)
    duration: Mapped[float] = mapped_column(default=0.0)

    run: Mapped["Run"] = relationship(back_populates="failures")