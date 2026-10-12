from sqlalchemy import text

from app.db import get_engine

with get_engine().begin() as conn:
    # enables vector support so we can store embeddings later
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    version = conn.execute(
        text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    ).scalar()
    print("pgvector version:", version)