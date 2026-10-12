from sqlalchemy import create_engine

from app.config import settings


def get_engine():
    # pool pre ping drops dead connections, which matters on serverless databases
    return create_engine(settings.database_url, pool_pre_ping=True)