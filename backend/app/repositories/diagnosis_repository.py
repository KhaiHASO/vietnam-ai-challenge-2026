from copy import deepcopy
from datetime import datetime
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
        try:
            return get_database()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail="MongoDB is not available") from exc

    async def insert_one(self, collection_name: str, document: dict[str, Any]) -> dict[str, Any]:
        if self.use_memory:
            stored = deepcopy(document)
            _MEMORY_STORE[collection_name].append(stored)
            return deepcopy(stored)

        await self.database[collection_name].insert_one(document)
        return _serialize_document(document) or document

    async def insert_many(
        self, collection_name: str, documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not documents:
            return []

        if self.use_memory:
            stored_docs = deepcopy(documents)
            _MEMORY_STORE[collection_name].extend(stored_docs)
            return deepcopy(stored_docs)

        await self.database[collection_name].insert_many(documents)
        return [_serialize_document(document) or document for document in documents]

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

        document = await self.database[collection_name].find_one(query, sort=sort)
        return _serialize_document(document)

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

        cursor = self.database[collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        return [_serialize_document(doc) async for doc in cursor]

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

        await self.database[collection_name].update_one(query, {"$set": update})
        return await self.find_one(collection_name, query)

    async def count(self, collection_name: str, query: dict[str, Any] | None = None) -> int:
        query = query or {}
        if self.use_memory:
            return len([doc for doc in _MEMORY_STORE[collection_name] if _matches(doc, query)])

        return await self.database[collection_name].count_documents(query)
