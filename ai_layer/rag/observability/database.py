import sqlite3
import os
import uuid
import time
from ai_layer.config import settings


class TelemetryDB:
    @staticmethod
    def log_span(span_id, trace_id, step_name, latency_ms, input_tokens, output_tokens, cost_usd):
        db_path = os.path.join(settings.domain_dir, "data", "telemetry.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS spans (
            span_id TEXT,
            trace_id TEXT,
            step_name TEXT,
            latency_ms INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd REAL
        )""")
        conn.execute(
            "INSERT INTO spans VALUES (?,?,?,?,?,?,?)",
            (span_id, trace_id, step_name, int(latency_ms), input_tokens, output_tokens, cost_usd),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def log_event(event_type, tenant_id, payload):
        pass
