import os
import json
import logging
from datetime import datetime
from typing import Any, Dict
from ai_layer.rag.observability.database import TelemetryDB

logger = logging.getLogger(__name__)

class AuditLogger:
    def log(self, category: str, action: str, actor: str, payload: Dict[str, Any] = None, result: Dict[str, Any] = None, trace_id: str = None):
        self._write_log(category.upper(), actor, {
            'action': action,
            'trace_id': trace_id,
            'payload': payload or {},
            'result': result or {},
        })

    def _write_log(self, event_type: str, tenant_id: str, payload: Dict[str, Any]):
        try:
            TelemetryDB.log_event(
                event_type=event_type,
                tenant_id=tenant_id,
                payload=payload
            )
        except Exception as e:
            logger.error(f'Failed to write audit log to telemetry db: {e}')

    def log_chat(self, tenant_id: str, session_id: str, domain: str, query: str, answer: str, processing_time_ms: int = 0):
        self._write_log('CHAT', tenant_id, {
            'session_id': session_id,
            'domain': domain,
            'query': query,
            'answer': answer,
            'processing_time_ms': processing_time_ms
        })

    def log_ingest(self, tenant_id: str, domain: str, source: str, document_id: str, chunks_count: int):
        self._write_log('INGEST', tenant_id, {
            'domain': domain,
            'source': source,
            'document_id': document_id,
            'chunks_count': chunks_count
        })

audit_logger = AuditLogger()
