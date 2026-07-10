import sqlite3
import os
from ai_layer.config import settings


def get_connection():
    db_path = os.path.join(settings.domain_dir, "data", "memory.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS evaluations (
        session_id TEXT,
        tenant_id TEXT,
        domain TEXT,
        prompt_version TEXT,
        query TEXT,
        faithfulness_score REAL,
        relevance_score REAL,
        latency REAL,
        timestamp TEXT
    )""")
    conn.commit()
    return conn
