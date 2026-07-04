import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("backend.mongo_schema")

ASCENDING = 1
DESCENDING = -1
VALIDATION_LEVEL = "moderate"
VALIDATION_ACTION = "warn"


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
    required: list[str],
    properties: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": required,
            "additionalProperties": True,
            "properties": properties,
        }
    }


def _base_props() -> dict[str, dict[str, Any]]:
    return {
        "created_at": {"bsonType": ["date", "string"]},
        "updated_at": {"bsonType": ["date", "string"]},
    }


COLLECTION_SPECS: tuple[CollectionSpec, ...] = (
    CollectionSpec(
        name="farms",
        validator=_json_schema(
            required=["farm_id", "name", "created_at"],
            properties={
                **_base_props(),
                "farm_id": {"bsonType": "string"},
                "owner_id": {"bsonType": "string"},
                "name": {"bsonType": "string"},
                "location": {"bsonType": ["object", "string"]},
                "crop_types": {"bsonType": "array"},
            },
        ),
    ),
    CollectionSpec(
        name="diagnosis_cases",
        validator=_json_schema(
            required=["case_id", "status", "created_at"],
            properties={
                **_base_props(),
                "case_id": {"bsonType": "string"},
                "farm_id": {"bsonType": "string"},
                "status": {"bsonType": "string"},
                "crop": {"bsonType": "string"},
                "risk_level": {"bsonType": "string"},
                "summary": {"bsonType": "string"},
            },
        ),
        indexes=(
            IndexSpec(
                name="idx_diagnosis_cases_case_id",
                keys=(("case_id", ASCENDING),),
            ),
            IndexSpec(
                name="idx_diagnosis_cases_status",
                keys=(("status", ASCENDING),),
            ),
            IndexSpec(
                name="idx_diagnosis_cases_created_at",
                keys=(("created_at", DESCENDING),),
            ),
        ),
    ),
    CollectionSpec(
        name="case_images",
        validator=_json_schema(
            required=["image_id", "case_id", "uri", "created_at"],
            properties={
                **_base_props(),
                "image_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "uri": {"bsonType": "string"},
                "content_type": {"bsonType": "string"},
                "metadata": {"bsonType": "object"},
            },
        ),
    ),
    CollectionSpec(
        name="vision_results",
        validator=_json_schema(
            required=["result_id", "case_id", "created_at"],
            properties={
                **_base_props(),
                "result_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "image_id": {"bsonType": "string"},
                "model_name": {"bsonType": "string"},
                "predictions": {"bsonType": "array"},
                "confidence": {"bsonType": ["double", "int", "long", "decimal"]},
            },
        ),
    ),
    CollectionSpec(
        name="symptom_questions",
        validator=_json_schema(
            required=["question_id", "case_id", "text", "created_at"],
            properties={
                **_base_props(),
                "question_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "text": {"bsonType": "string"},
                "options": {"bsonType": "array"},
            },
        ),
    ),
    CollectionSpec(
        name="symptom_answers",
        validator=_json_schema(
            required=["answer_id", "question_id", "case_id", "created_at"],
            properties={
                **_base_props(),
                "answer_id": {"bsonType": "string"},
                "question_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "answer": {"bsonType": ["string", "object", "array"]},
            },
        ),
    ),
    CollectionSpec(
        name="treatment_plans",
        validator=_json_schema(
            required=["plan_id", "case_id", "status", "created_at"],
            properties={
                **_base_props(),
                "plan_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "status": {"bsonType": "string"},
                "recommendations": {"bsonType": "array"},
                "safety_notes": {"bsonType": "array"},
            },
        ),
    ),
    CollectionSpec(
        name="expert_reviews",
        validator=_json_schema(
            required=["review_id", "case_id", "status", "created_at"],
            properties={
                **_base_props(),
                "review_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "status": {"bsonType": "string"},
                "reviewer_id": {"bsonType": "string"},
                "notes": {"bsonType": "string"},
            },
        ),
        indexes=(
            IndexSpec(
                name="idx_expert_reviews_status",
                keys=(("status", ASCENDING),),
            ),
        ),
    ),
    CollectionSpec(
        name="agent_logs",
        validator=_json_schema(
            required=["log_id", "case_id", "agent", "status", "created_at"],
            properties={
                **_base_props(),
                "log_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "agent": {"bsonType": "string"},
                "status": {"bsonType": "string"},
                "trace": {"bsonType": ["array", "object"]},
                "duration_ms": {"bsonType": ["double", "int", "long", "decimal"]},
            },
        ),
        indexes=(
            IndexSpec(
                name="idx_agent_logs_case_id",
                keys=(("case_id", ASCENDING),),
            ),
        ),
    ),
    CollectionSpec(
        name="season_logs",
        validator=_json_schema(
            required=["season_log_id", "farm_id", "created_at"],
            properties={
                **_base_props(),
                "season_log_id": {"bsonType": "string"},
                "farm_id": {"bsonType": "string"},
                "season": {"bsonType": "string"},
                "notes": {"bsonType": "string"},
                "metrics": {"bsonType": "object"},
            },
        ),
    ),
    CollectionSpec(
        name="reminders",
        validator=_json_schema(
            required=["reminder_id", "status", "created_at"],
            properties={
                **_base_props(),
                "reminder_id": {"bsonType": "string"},
                "farm_id": {"bsonType": "string"},
                "case_id": {"bsonType": "string"},
                "due_at": {"bsonType": ["date", "string"]},
                "status": {"bsonType": "string"},
                "message": {"bsonType": "string"},
            },
        ),
    ),
    CollectionSpec(
        name="model_reports",
        validator=_json_schema(
            required=["report_id", "model_name", "created_at"],
            properties={
                **_base_props(),
                "report_id": {"bsonType": "string"},
                "model_name": {"bsonType": "string"},
                "model_version": {"bsonType": "string"},
                "metrics": {"bsonType": "object"},
                "notes": {"bsonType": "string"},
            },
        ),
    ),
)

REQUIRED_COLLECTION_NAMES = tuple(spec.name for spec in COLLECTION_SPECS)


async def ensure_mongo_schema(database: Any) -> dict[str, Any]:
    existing_collections = set(await database.list_collection_names())
    report: dict[str, Any] = {
        "collections": [],
        "indexes": {},
        "errors": [],
    }

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
                list(index.keys),
                name=index.name,
                **index.options,
            )
            report["indexes"][spec.name].append(index.name)

    return report
