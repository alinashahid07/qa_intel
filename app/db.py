from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.config import settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    # pool pre ping drops dead connections which matters on serverless databases
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_db():
    # gives each request its own session and always closes it afterwards
    with Session(get_engine(), autoflush=False) as db:
        yield db