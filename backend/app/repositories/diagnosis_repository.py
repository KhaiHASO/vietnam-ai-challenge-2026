from copy import deepcopy
from datetime import datetime
import logging
from typing import Any

from fastapi import HTTPException

from app.core.config import settings
from app.db.mongo import get_database, mongo_state

COLLECTIONS = (
    "farms",
    "diagnosis_cases",
    "case_images",
    "vision_results",
    "symptom_questions",
    "symptom_answers",
    "treatment_plans",
    "expert_reviews",
    "agent_logs",
    "season_logs",
    "reminders",
    "model_reports",
)

logger = logging.getLogger("backend.diagnosis_repository")

MONGO_UNAVAILABLE_DETAIL = {
    "code": "MONGO_UNAVAILABLE",
    "message": "MongoDB is not available; try again later or enable DEMO_MODE.",
}

MONGO_OPERATION_FAILED_DETAIL = {
    "code": "MONGO_OPERATION_FAILED",
    "message": "MongoDB operation failed gracefully; try again later.",
}

_MEMORY_STORE: dict[str, list[dict[str, Any]]] = {name: [] for name in COLLECTIONS}


def _serialize_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    clean = dict(document)
    if "_id" in clean:
        clean["_id"] = str(clean["_id"])
    return clean


def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
    return all(document.get(key) == value for key, value in query.items())


class DiagnosisRepository:
    def __init__(self) -> None:
        self.use_memory = settings.demo_mode and not mongo_state.connected

    @property
    def database(self):
        if self.use_memory:
            return None
        if not mongo_state.connected:
            raise HTTPException(status_code=503, detail=MONGO_UNAVAILABLE_DETAIL)
        try:
            return get_database()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=MONGO_UNAVAILABLE_DETAIL) from exc

    def _handle_mongo_error(self, operation: str, exc: Exception) -> None:
        logger.warning("MongoDB %s failed: %s", operation, exc.__class__.__name__)
        mongo_state.last_error = exc.__class__.__name__
        raise HTTPException(status_code=503, detail=MONGO_OPERATION_FAILED_DETAIL) from exc

    async def insert_one(self, collection_name: str, document: dict[str, Any]) -> dict[str, Any]:
        if self.use_memory:
            stored = deepcopy(document)
            _MEMORY_STORE[collection_name].append(stored)
            return deepcopy(stored)

        try:
            await self.database[collection_name].insert_one(document)
            return _serialize_document(document) or document
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("insert_one", exc)

    async def insert_many(
        self, collection_name: str, documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not documents:
            return []

        if self.use_memory:
            stored_docs = deepcopy(documents)
            _MEMORY_STORE[collection_name].extend(stored_docs)
            return deepcopy(stored_docs)

        try:
            await self.database[collection_name].insert_many(documents)
            return [_serialize_document(document) or document for document in documents]
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("insert_many", exc)

    async def find_one(
        self,
        collection_name: str,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
    ) -> dict[str, Any] | None:
        if self.use_memory:
            matches = [doc for doc in _MEMORY_STORE[collection_name] if _matches(doc, query)]
            if sort:
                for field, direction in reversed(sort):
                    matches.sort(
                        key=lambda item: item.get(field, datetime.min),
                        reverse=direction < 0,
                    )
            return deepcopy(matches[0]) if matches else None

        try:
            document = await self.database[collection_name].find_one(query, sort=sort)
            return _serialize_document(document)
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("find_one", exc)

    async def find_many(
        self,
        collection_name: str,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        if self.use_memory:
            matches = [doc for doc in _MEMORY_STORE[collection_name] if _matches(doc, query)]
            if sort:
                for field, direction in reversed(sort):
                    matches.sort(
                        key=lambda item: item.get(field, datetime.min),
                        reverse=direction < 0,
                    )
            return deepcopy(matches)

        try:
            cursor = self.database[collection_name].find(query)
            if sort:
                cursor = cursor.sort(sort)
            return [_serialize_document(doc) async for doc in cursor]
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("find_many", exc)

    async def update_one(
        self,
        collection_name: str,
        query: dict[str, Any],
        update: dict[str, Any],
    ) -> dict[str, Any] | None:
        if self.use_memory:
            for index, document in enumerate(_MEMORY_STORE[collection_name]):
                if _matches(document, query):
                    updated = deepcopy(document)
                    updated.update(update)
                    _MEMORY_STORE[collection_name][index] = updated
                    return deepcopy(updated)
            return None

        try:
            await self.database[collection_name].update_one(query, {"$set": update})
            return await self.find_one(collection_name, query)
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("update_one", exc)

    async def count(self, collection_name: str, query: dict[str, Any] | None = None) -> int:
        query = query or {}
        if self.use_memory:
            return len([doc for doc in _MEMORY_STORE[collection_name] if _matches(doc, query)])

        try:
            return await self.database[collection_name].count_documents(query)
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("count", exc)

    async def delete_one(
        self,
        collection_name: str,
        query: dict[str, Any],
    ) -> bool:
        if self.use_memory:
            for index, document in enumerate(_MEMORY_STORE[collection_name]):
                if _matches(document, query):
                    _MEMORY_STORE[collection_name].pop(index)
                    return True
            return False

        try:
            res = await self.database[collection_name].delete_one(query)
            return res.deleted_count > 0
        except HTTPException:
            raise
        except Exception as exc:
            self._handle_mongo_error("delete_one", exc)
