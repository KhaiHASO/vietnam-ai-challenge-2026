from __future__ import annotations

import asyncio
import hashlib
import json

from .contracts import AttemptEvent, LearnerSkillState, LearnerStateEvent


class AttemptIdempotencyConflict(ValueError):
    pass


class LearnerStateRevisionConflict(ValueError):
    pass


def _attempt_fingerprint(event: AttemptEvent) -> str:
    payload = event.model_dump(
        mode="json", exclude={"attempt_id", "created_at"}
    )
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class InMemoryAttemptRepository:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], AttemptEvent] = {}
        self._fingerprints: dict[tuple[str, str], str] = {}
        self._attempt_ids: set[tuple[str, str]] = set()

    async def append(self, event: AttemptEvent) -> AttemptEvent:
        idempotency_scope = (event.tenant_id, event.idempotency_key)
        fingerprint = _attempt_fingerprint(event)
        existing = self._events.get(idempotency_scope)
        if existing is not None:
            if self._fingerprints[idempotency_scope] != fingerprint:
                raise AttemptIdempotencyConflict(
                    "idempotency key was already used for another attempt payload"
                )
            return existing

        attempt_scope = (event.tenant_id, event.attempt_id)
        if attempt_scope in self._attempt_ids:
            raise AttemptIdempotencyConflict("attempt ID already exists in tenant")
        self._attempt_ids.add(attempt_scope)
        self._events[idempotency_scope] = event
        self._fingerprints[idempotency_scope] = fingerprint
        return event

    async def get(self, tenant_id: str, attempt_id: str) -> AttemptEvent | None:
        for event in self._events.values():
            if event.tenant_id == tenant_id and event.attempt_id == attempt_id:
                return event
        return None

    async def list_for_student(
        self, tenant_id: str, student_id: str
    ) -> list[AttemptEvent]:
        return sorted(
            (
                event
                for event in self._events.values()
                if event.tenant_id == tenant_id and event.student_id == student_id
            ),
            key=lambda event: (event.created_at, event.step_index, event.attempt_id),
        )


class InMemoryLearnerStateRepository:
    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str, str], LearnerSkillState] = {}
        self._events: list[LearnerStateEvent] = []
        self._event_sources: dict[
            tuple[str, str, str, str, str], LearnerStateEvent
        ] = {}
        self._commit_lock = asyncio.Lock()

    @staticmethod
    def _event_source_key(
        event: LearnerStateEvent,
    ) -> tuple[str, str, str, str, str]:
        source = event.source_attempt_id or event.event_id
        return (
            event.tenant_id,
            event.student_id,
            event.skill_id,
            event.event_type,
            source,
        )

    async def get(
        self, tenant_id: str, student_id: str, skill_id: str
    ) -> LearnerSkillState | None:
        return self._snapshots.get((tenant_id, student_id, skill_id))

    async def save(
        self, state: LearnerSkillState, *, expected_revision: int
    ) -> LearnerSkillState:
        key = (state.tenant_id, state.student_id, state.skill_id)
        current = self._snapshots.get(key)
        current_revision = current.revision if current else -1
        if current_revision != expected_revision:
            raise LearnerStateRevisionConflict(
                f"expected revision {expected_revision}, got {current_revision}"
            )
        if state.revision != expected_revision + 1:
            raise LearnerStateRevisionConflict(
                f"next snapshot revision must be {expected_revision + 1}"
            )
        self._snapshots[key] = state
        return state

    async def append_event(self, event: LearnerStateEvent) -> LearnerStateEvent:
        key = self._event_source_key(event)
        existing = self._event_sources.get(key)
        if existing is not None:
            return existing
        self._events.append(event)
        self._event_sources[key] = event
        return event

    async def get_event_for_source(
        self,
        tenant_id: str,
        student_id: str,
        skill_id: str,
        event_type: str,
        source_attempt_id: str,
    ) -> LearnerStateEvent | None:
        return self._event_sources.get(
            (
                tenant_id,
                student_id,
                skill_id,
                event_type,
                source_attempt_id,
            )
        )

    async def commit_event(
        self,
        state: LearnerSkillState,
        event: LearnerStateEvent,
        *,
        expected_revision: int,
    ) -> tuple[LearnerSkillState, bool]:
        """Atomically compare-and-swap a snapshot with its source event."""

        async with self._commit_lock:
            event_key = self._event_source_key(event)
            snapshot_key = (state.tenant_id, state.student_id, state.skill_id)
            existing_event = self._event_sources.get(event_key)
            if existing_event is not None:
                current = self._snapshots.get(snapshot_key)
                if current is None:
                    raise LearnerStateRevisionConflict(
                        "source event exists without learner snapshot"
                    )
                return current, False

            if (
                event.tenant_id,
                event.student_id,
                event.skill_id,
            ) != snapshot_key:
                raise LearnerStateRevisionConflict(
                    "state event scope does not match snapshot"
                )
            current = self._snapshots.get(snapshot_key)
            current_revision = current.revision if current else -1
            if current_revision != expected_revision:
                raise LearnerStateRevisionConflict(
                    f"expected revision {expected_revision}, got {current_revision}"
                )
            if state.revision != expected_revision + 1:
                raise LearnerStateRevisionConflict(
                    f"next snapshot revision must be {expected_revision + 1}"
                )
            if event.resulting_revision != state.revision:
                raise LearnerStateRevisionConflict(
                    "state event revision does not match snapshot revision"
                )

            self._snapshots[snapshot_key] = state
            self._events.append(event)
            self._event_sources[event_key] = event
            return state, True

    async def list_events(
        self, tenant_id: str, student_id: str, skill_id: str
    ) -> list[LearnerStateEvent]:
        return [
            event
            for event in self._events
            if event.tenant_id == tenant_id
            and event.student_id == student_id
            and event.skill_id == skill_id
        ]
