import logging
from dataclasses import dataclass, field
from typing import Any


logger = logging.getLogger("backend.mongo_schema")

ASCENDING = 1
DESCENDING = -1
VALIDATION_LEVEL = "moderate"
VALIDATION_ACTION = "error"


@dataclass(frozen=True)
class IndexSpec:
    name: str
    keys: tuple[tuple[str, int], ...]
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CollectionSpec:
    name: str
    validator: dict[str, Any]
    indexes: tuple[IndexSpec, ...] = ()


def _json_schema(
    required: list[str], properties: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": required,
            "additionalProperties": True,
            "properties": {
                "created_at": {"bsonType": ["date", "string"]},
                "updated_at": {"bsonType": ["date", "string"]},
                **properties,
            },
        }
    }


def _string_fields(*names: str) -> dict[str, dict[str, Any]]:
    return {name: {"bsonType": "string"} for name in names}


COLLECTION_SPECS: tuple[CollectionSpec, ...] = (
    CollectionSpec(
        name="students",
        validator=_json_schema(
            ["tenant_id", "student_id", "pseudonym", "created_at"],
            {
                **_string_fields("tenant_id", "student_id", "pseudonym"),
                "grade": {"bsonType": ["int", "long"]},
                "class_ids": {"bsonType": "array"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_students_scope",
                (("tenant_id", ASCENDING), ("student_id", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_students_pseudonym",
                (("tenant_id", ASCENDING), ("pseudonym", ASCENDING)),
                {"unique": True},
            ),
        ),
    ),
    CollectionSpec(
        name="classes",
        validator=_json_schema(
            ["tenant_id", "class_id", "teacher_ids", "created_at"],
            {
                **_string_fields("tenant_id", "class_id", "name"),
                "teacher_ids": {"bsonType": "array"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_classes_scope",
                (("tenant_id", ASCENDING), ("class_id", ASCENDING)),
                {"unique": True},
            ),
        ),
    ),
    CollectionSpec(
        name="class_enrollments",
        validator=_json_schema(
            ["tenant_id", "class_id", "student_id", "created_at"],
            _string_fields("tenant_id", "class_id", "student_id"),
        ),
        indexes=(
            IndexSpec(
                "idx_enrollment_scope",
                (
                    ("tenant_id", ASCENDING),
                    ("class_id", ASCENDING),
                    ("student_id", ASCENDING),
                ),
                {"unique": True},
            ),
        ),
    ),
    CollectionSpec(
        name="questions",
        validator=_json_schema(
            ["tenant_id", "question_id", "skill_ids", "version", "created_at"],
            {
                **_string_fields("tenant_id", "question_id", "version", "status"),
                "skill_ids": {"bsonType": "array"},
                "prompt": {"bsonType": "string"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_questions_version",
                (
                    ("tenant_id", ASCENDING),
                    ("question_id", ASCENDING),
                    ("version", ASCENDING),
                ),
                {"unique": True},
            ),
            IndexSpec(
                "idx_questions_skills",
                (("tenant_id", ASCENDING), ("skill_ids", ASCENDING)),
            ),
        ),
    ),
    CollectionSpec(
        name="practice_sessions",
        validator=_json_schema(
            [
                "tenant_id",
                "session_id",
                "student_id",
                "target_skill_id",
                "versions",
                "created_at",
            ],
            {
                **_string_fields(
                    "tenant_id", "session_id", "student_id", "target_skill_id", "status"
                ),
                "versions": {"bsonType": "object"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_practice_sessions_scope",
                (("tenant_id", ASCENDING), ("session_id", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_practice_sessions_student",
                (
                    ("tenant_id", ASCENDING),
                    ("student_id", ASCENDING),
                    ("created_at", DESCENDING),
                ),
            ),
        ),
    ),
    CollectionSpec(
        name="attempt_events",
        validator=_json_schema(
            [
                "attempt_id",
                "tenant_id",
                "student_id",
                "session_id",
                "question_id",
                "skill_id",
                "verification_status",
                "idempotency_key",
                "created_at",
            ],
            {
                **_string_fields(
                    "attempt_id",
                    "tenant_id",
                    "student_id",
                    "session_id",
                    "question_id",
                    "skill_id",
                    "verification_status",
                    "idempotency_key",
                    "graph_version",
                    "question_version",
                    "policy_version",
                    "model_version",
                ),
                "step_index": {"bsonType": ["int", "long"]},
                "raw_step": {"bsonType": "string"},
                "evidence": {"bsonType": "object"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_attempt_events_tenant_idempotency",
                (("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_attempt_events_id",
                (("tenant_id", ASCENDING), ("attempt_id", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_attempt_events_student_skill",
                (
                    ("tenant_id", ASCENDING),
                    ("student_id", ASCENDING),
                    ("skill_id", ASCENDING),
                    ("created_at", ASCENDING),
                ),
            ),
        ),
    ),
    CollectionSpec(
        name="learner_state_events",
        validator=_json_schema(
            [
                "event_id",
                "tenant_id",
                "student_id",
                "skill_id",
                "event_type",
                "resulting_revision",
                "occurred_at",
            ],
            {
                **_string_fields(
                    "event_id", "tenant_id", "student_id", "skill_id", "event_type"
                ),
                "source_attempt_id": {"bsonType": ["string", "null"]},
                "resulting_revision": {"bsonType": ["int", "long"]},
                "occurred_at": {"bsonType": ["date", "string"]},
                "payload": {"bsonType": "object"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_learner_state_events_id",
                (("tenant_id", ASCENDING), ("event_id", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_learner_state_events_source",
                (
                    ("tenant_id", ASCENDING),
                    ("student_id", ASCENDING),
                    ("skill_id", ASCENDING),
                    ("event_type", ASCENDING),
                    ("source_attempt_id", ASCENDING),
                ),
                {"unique": True, "sparse": True},
            ),
        ),
    ),
    CollectionSpec(
        name="learner_state_snapshots",
        validator=_json_schema(
            [
                "tenant_id",
                "student_id",
                "skill_id",
                "mastery",
                "confidence",
                "evidence_count",
                "revision",
                "updated_at",
            ],
            {
                **_string_fields(
                    "tenant_id", "student_id", "skill_id", "graph_version", "model_version"
                ),
                "mastery": {"bsonType": ["double", "int", "long", "decimal"]},
                "confidence": {"bsonType": ["double", "int", "long", "decimal"]},
                "evidence_count": {"bsonType": ["int", "long"]},
                "revision": {"bsonType": ["int", "long"]},
                "source_attempt_ids": {"bsonType": "array"},
                "recent_misconceptions": {"bsonType": "object"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_learner_state_scope",
                (
                    ("tenant_id", ASCENDING),
                    ("student_id", ASCENDING),
                    ("skill_id", ASCENDING),
                ),
                {"unique": True},
            ),
        ),
    ),
    CollectionSpec(
        name="users",
        validator=_json_schema(
            [
                "user_id",
                "tenant_id",
                "username",
                "normalized_username",
                "hashed_password",
                "roles",
                "created_at",
            ],
            {
                **_string_fields(
                    "user_id", "tenant_id", "username", "normalized_username", "hashed_password"
                ),
                "email": {"bsonType": ["string", "null"]},
                "roles": {"bsonType": "array"},
                "is_active": {"bsonType": "bool"},
            },
        ),
        indexes=(
            IndexSpec(
                "idx_users_username_unique",
                (("tenant_id", ASCENDING), ("normalized_username", ASCENDING)),
                {"unique": True},
            ),
            IndexSpec(
                "idx_users_email_unique",
                (("tenant_id", ASCENDING), ("email", ASCENDING)),
                {"unique": True, "sparse": True},
            ),
        ),
    ),
    CollectionSpec(
        name="refresh_sessions",
        validator=_json_schema(
            ["token_id", "family_id", "user_id", "tenant_id", "hashed_token", "expires_at", "created_at"],
            {
                **_string_fields("token_id", "family_id", "user_id", "tenant_id", "hashed_token"),
                "expires_at": {"bsonType": "date"},
                "revoked": {"bsonType": "bool"},
                "consumed_at": {"bsonType": ["date", "null"]},
            },
        ),
        indexes=(
            IndexSpec("idx_refresh_token_hash", (("hashed_token", ASCENDING),), {"unique": True}),
            IndexSpec("idx_refresh_expiry_ttl", (("expires_at", ASCENDING),), {"expireAfterSeconds": 0}),
        ),
    ),
    CollectionSpec(
        name="refresh_families",
        validator=_json_schema(
            ["family_id", "revoked", "updated_at"],
            {**_string_fields("family_id"), "revoked": {"bsonType": "bool"}},
        ),
        indexes=(IndexSpec("idx_refresh_family", (("family_id", ASCENDING),), {"unique": True}),),
    ),
    CollectionSpec(
        name="audit_events",
        validator=_json_schema(
            ["event_id", "event_type", "occurred_at"],
            {**_string_fields("event_id", "event_type", "tenant_id", "user_id")},
        ),
        indexes=(IndexSpec("idx_audit_time", (("occurred_at", DESCENDING),)),),
    ),
    CollectionSpec(
        name="jobs",
        validator=_json_schema(
            ["job_id", "job_type", "idempotency_key", "payload", "attempts", "status", "next_run_at"],
            {
                **_string_fields("job_id", "job_type", "idempotency_key", "status"),
                "payload": {"bsonType": "object"},
                "attempts": {"bsonType": ["int", "long"]},
                "next_run_at": {"bsonType": "date"},
            },
        ),
        indexes=(
            IndexSpec("idx_jobs_id", (("job_id", ASCENDING),), {"unique": True}),
            IndexSpec("idx_jobs_idempotency", (("idempotency_key", ASCENDING),), {"unique": True}),
            IndexSpec("idx_jobs_ready", (("status", ASCENDING), ("next_run_at", ASCENDING))),
        ),
    ),
    CollectionSpec(
        name="approvals",
        validator=_json_schema(
            ["approval_id", "policy", "requester", "status"],
            {
                **_string_fields("approval_id", "policy", "requester", "status"),
                "proposed_action": {"bsonType": "object"},
                "evidence": {"bsonType": "array"},
            },
        ),
        indexes=(IndexSpec("idx_approvals_id", (("approval_id", ASCENDING),), {"unique": True}),),
    ),
    CollectionSpec(
        name="memory_facts",
        validator=_json_schema(
            ["fact_id", "tenant_id", "domain_id", "user_id", "key", "status", "created_at"],
            _string_fields("fact_id", "tenant_id", "domain_id", "user_id", "key", "status"),
        ),
        indexes=(
            IndexSpec("idx_memory_id", (("fact_id", ASCENDING),), {"unique": True}),
            IndexSpec("idx_memory_scope", (("tenant_id", ASCENDING), ("domain_id", ASCENDING), ("user_id", ASCENDING))),
        ),
    ),
    CollectionSpec(
        name="idempotency_records",
        validator=_json_schema(
            ["idempotency_key", "request_hash", "status", "created_at"],
            _string_fields("idempotency_key", "request_hash", "status"),
        ),
        indexes=(
            IndexSpec("idx_idempotency_key", (("idempotency_key", ASCENDING),), {"unique": True}),
            IndexSpec("idx_idempotency_ttl", (("created_at", ASCENDING),), {"expireAfterSeconds": 86400}),
        ),
    ),
    CollectionSpec(
        name="copilot_sessions",
        validator=_json_schema(
            ["session_id", "tenant_id", "user_id", "revision", "created_at"],
            {
                **_string_fields("session_id", "tenant_id", "user_id"),
                "revision": {"bsonType": ["int", "long"]},
            },
        ),
        indexes=(IndexSpec("idx_copilot_session", (("session_id", ASCENDING),), {"unique": True}),),
    ),
    CollectionSpec(
        name="copilot_messages",
        validator=_json_schema(
            ["message_id", "session_id", "sequence", "role", "content", "created_at"],
            {
                **_string_fields("message_id", "session_id", "role", "content"),
                "sequence": {"bsonType": ["int", "long"]},
            },
        ),
        indexes=(IndexSpec("idx_copilot_message_seq", (("session_id", ASCENDING), ("sequence", ASCENDING)), {"unique": True}),),
    ),
    CollectionSpec(
        name="copilot_events",
        validator=_json_schema(
            ["event_id", "session_id", "sequence", "type", "timestamp"],
            {
                **_string_fields("event_id", "session_id", "type"),
                "sequence": {"bsonType": ["int", "long"]},
                "timestamp": {"bsonType": "date"},
            },
        ),
        indexes=(IndexSpec("idx_copilot_event_seq", (("session_id", ASCENDING), ("sequence", ASCENDING))),),
    ),
)


REQUIRED_COLLECTION_NAMES = tuple(spec.name for spec in COLLECTION_SPECS)


async def ensure_mongo_schema(database: Any) -> dict[str, Any]:
    existing_collections = set(await database.list_collection_names())
    report: dict[str, Any] = {"collections": [], "indexes": {}, "errors": []}

    for spec in COLLECTION_SPECS:
        if spec.name not in existing_collections:
            await database.create_collection(
                spec.name,
                validator=spec.validator,
                validationLevel=VALIDATION_LEVEL,
                validationAction=VALIDATION_ACTION,
            )
        else:
            try:
                await database.command(
                    {
                        "collMod": spec.name,
                        "validator": spec.validator,
                        "validationLevel": VALIDATION_LEVEL,
                        "validationAction": VALIDATION_ACTION,
                    }
                )
            except Exception as exc:
                message = f"{spec.name}: {exc.__class__.__name__}"
                logger.warning("Could not update MongoDB validator for %s", message)
                report["errors"].append(message)

        report["collections"].append(spec.name)
        report["indexes"][spec.name] = []
        for index in spec.indexes:
            await database[spec.name].create_index(
                list(index.keys), name=index.name, **index.options
            )
            report["indexes"][spec.name].append(index.name)

    return report
