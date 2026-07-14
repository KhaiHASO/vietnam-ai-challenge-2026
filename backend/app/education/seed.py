from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_layer.rag.registries.curriculum_graph import load_curriculum_graph


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GRAPH_PATH = (
    PROJECT_ROOT
    / "domains"
    / "education-mathpath"
    / "knowledge"
    / "curriculum_graph.yaml"
)
FORBIDDEN_STUDENT_IDENTITY_FIELDS = {
    "address",
    "date_of_birth",
    "email",
    "external_id",
    "full_name",
    "name",
    "phone",
    "phone_number",
    "school_identifier",
    "student_code",
}


class SeedPrivacyError(ValueError):
    pass


class SeedConflict(ValueError):
    pass


class _SeedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SeedClass(_SeedModel):
    class_id: str
    label: str
    grade: Literal[10, 11, 12]
    teacher_id: str


class SeedStudent(_SeedModel):
    student_id: str
    pseudonym: str
    grade: Literal[10, 11, 12]
    class_id: str


class SeedQuestion(_SeedModel):
    question_id: str
    skill_id: str
    version: str
    prompt: str
    difficulty: Literal["foundation", "core", "challenge"]


class SeedAttempt(_SeedModel):
    attempt_id: str
    student_id: str
    question_id: str
    skill_id: str
    step_index: int = Field(ge=0)
    raw_step: str
    verification_status: Literal[
        "verified", "contradicted", "unsupported", "timeout"
    ]
    misconception_id: str | None = None
    hint_level: int = Field(default=0, ge=0, le=3)
    trace_id: str


class SeedJourney(_SeedModel):
    journey_id: str
    kind: Literal[
        "correct-progress",
        "prerequisite-gap",
        "repeated-misconception",
        "hint-escalation",
        "teacher-intervention",
    ]
    title_vi: str
    student_id: str
    attempt_ids: tuple[str, ...]
    expected_checkpoints: tuple[str, ...]
    trace_id: str


class MathPathSeed(_SeedModel):
    dataset_version: str
    deterministic_seed: int
    tenant_id: str
    graph_version: str
    generated_at: str
    classes: list[SeedClass]
    students: list[SeedStudent]
    questions: list[SeedQuestion]
    attempts: list[SeedAttempt]
    journeys: list[SeedJourney]


@dataclass(frozen=True)
class SeedValidationReport:
    dataset_version: str
    checksum: str
    student_count: int
    question_count: int
    attempt_count: int
    journey_count: int
    errors: tuple[str, ...]


_QUESTION_BLUEPRINTS = (
    ("A10-ALG-08", "Nêu điều kiện xác định của (x+1)/(x-1).", "foundation"),
    ("A10-ALG-07", "Rút gọn một phân thức và ghi rõ điều kiện đi kèm.", "core"),
    ("A11-CAL-03", "Dùng định nghĩa để giải thích đạo hàm tại một điểm.", "core"),
    ("A11-CAL-04", "Tính đạo hàm của một tổng đa thức.", "foundation"),
    ("A11-CAL-05", "Tính đạo hàm của x²/(x-1).", "core"),
    ("A11-CAL-06", "Tính đạo hàm của (2x+1)³.", "core"),
    ("A11-CAL-07", "Tính đạo hàm hàm phân thức và giữ tập xác định.", "challenge"),
    ("A12-CAL-01", "Xét khoảng đồng biến của một hàm hữu tỉ.", "challenge"),
    ("A12-CAL-02", "Tìm cực trị bằng bảng dấu đạo hàm.", "challenge"),
    ("G10-GEO-03", "Lập phương trình đường thẳng qua hai điểm.", "core"),
    ("G10-PRO-02", "Tính xác suất từ một không gian mẫu hữu hạn.", "foundation"),
    ("G12-PRO-01", "Tính một xác suất có điều kiện đơn giản.", "core"),
)


def build_mathpath_seed(*, seed: int = 2026) -> MathPathSeed:
    rng = random.Random(seed)
    graph = load_curriculum_graph(GRAPH_PATH)
    graph_ids = {node.id for node in graph.nodes}
    if any(skill_id not in graph_ids for skill_id, _, _ in _QUESTION_BLUEPRINTS):
        raise SeedConflict("question blueprint references a missing curriculum skill")

    classes = [
        SeedClass(class_id="CLASS-10A1", label="Lớp demo 10A1", grade=10, teacher_id="TEACHER-01"),
        SeedClass(class_id="CLASS-11A1", label="Lớp demo 11A1", grade=11, teacher_id="TEACHER-01"),
        SeedClass(class_id="CLASS-12A1", label="Lớp demo 12A1", grade=12, teacher_id="TEACHER-02"),
    ]
    students = [
        SeedStudent(
            student_id=f"STU-{index:03d}",
            pseudonym=f"MP26-S{index:03d}",
            grade=classes[(index - 1) % len(classes)].grade,
            class_id=classes[(index - 1) % len(classes)].class_id,
        )
        for index in range(1, 37)
    ]
    questions = [
        SeedQuestion(
            question_id=f"Q-{index:03d}",
            skill_id=skill_id,
            version="questions-v1",
            prompt=prompt,
            difficulty=difficulty,
        )
        for index, (skill_id, prompt, difficulty) in enumerate(
            _QUESTION_BLUEPRINTS, start=1
        )
    ]

    attempts: list[SeedAttempt] = []
    statuses = ["verified", "verified", "contradicted", "verified"]
    for student_index, student in enumerate(students, start=1):
        for offset in range(2):
            attempt_number = (student_index - 1) * 2 + offset + 1
            question = questions[(student_index + offset - 1) % len(questions)]
            status = rng.choice(statuses)
            misconception = (
                "lost-domain-restriction" if status == "contradicted" else None
            )
            attempts.append(
                SeedAttempt(
                    attempt_id=f"ATT-{attempt_number:04d}",
                    student_id=student.student_id,
                    question_id=question.question_id,
                    skill_id=question.skill_id,
                    step_index=offset,
                    raw_step=(
                        "x != 1; áp dụng quy tắc thương"
                        if status == "verified"
                        else "bỏ điều kiện x != 1 khi biến đổi"
                    ),
                    verification_status=status,
                    misconception_id=misconception,
                    hint_level=1 if status == "contradicted" else 0,
                    trace_id=f"TRACE-SEED-{attempt_number:04d}",
                )
            )

    # Freeze the first five learners into the five named demo stories.
    forced = {
        0: ("verified", None, 0),
        2: ("contradicted", "lost-domain-restriction", 1),
        4: ("contradicted", "quotient-rule-numerator", 1),
        5: ("contradicted", "quotient-rule-numerator", 2),
        6: ("contradicted", "chain-rule-omission", 3),
        8: ("contradicted", "persistent-prerequisite-gap", 1),
    }
    for index, (status, misconception, hint_level) in forced.items():
        attempts[index] = attempts[index].model_copy(
            update={
                "verification_status": status,
                "misconception_id": misconception,
                "hint_level": hint_level,
            }
        )

    checkpoints = (
        "attempt",
        "verification",
        "diagnosis",
        "hint",
        "state-update",
        "teacher-insight",
    )
    journey_specs = (
        ("correct-progress", "Tiến bộ sau bước giải đúng", "STU-001", ("ATT-0001", "ATT-0002")),
        ("prerequisite-gap", "Phát hiện hổng điều kiện phân thức", "STU-002", ("ATT-0003", "ATT-0004")),
        ("repeated-misconception", "Lặp lại sai lầm quy tắc thương", "STU-003", ("ATT-0005", "ATT-0006")),
        ("hint-escalation", "Tăng dần mức gợi ý Socratic", "STU-004", ("ATT-0007", "ATT-0008")),
        ("teacher-intervention", "Giáo viên duyệt can thiệp", "STU-005", ("ATT-0009", "ATT-0010")),
    )
    journeys = [
        SeedJourney(
            journey_id=f"JOURNEY-{index:02d}",
            kind=kind,
            title_vi=title,
            student_id=student_id,
            attempt_ids=attempt_ids,
            expected_checkpoints=checkpoints,
            trace_id=f"TRACE-JOURNEY-{index:02d}",
        )
        for index, (kind, title, student_id, attempt_ids) in enumerate(
            journey_specs, start=1
        )
    ]

    return MathPathSeed(
        dataset_version="mathpath-seed-v1",
        deterministic_seed=seed,
        tenant_id="tenant-demo",
        graph_version=graph.revision,
        generated_at="2026-07-14T00:00:00+07:00",
        classes=classes,
        students=students,
        questions=questions,
        attempts=attempts,
        journeys=journeys,
    )


def _duplicates(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def validate_mathpath_seed(dataset: MathPathSeed) -> SeedValidationReport:
    for index, student in enumerate(dataset.students):
        forbidden = FORBIDDEN_STUDENT_IDENTITY_FIELDS & vars(student).keys()
        if forbidden:
            raise SeedPrivacyError(
                f"student[{index}] contains forbidden identity field(s): "
                f"{', '.join(sorted(forbidden))}"
            )

    errors: list[str] = []
    graph = load_curriculum_graph(GRAPH_PATH)
    graph_ids = {node.id for node in graph.nodes if node.active}
    class_ids = {item.class_id for item in dataset.classes}
    student_ids = {item.student_id for item in dataset.students}
    question_ids = {item.question_id for item in dataset.questions}
    attempt_ids = {item.attempt_id for item in dataset.attempts}

    if dataset.graph_version != graph.revision:
        errors.append(
            f"seed graph version {dataset.graph_version} != active {graph.revision}"
        )
    if len(dataset.students) < 30:
        errors.append("seed must contain at least 30 students")
    if len(dataset.journeys) != 5:
        errors.append("seed must contain exactly five named journeys")

    for label, values in (
        ("class", [item.class_id for item in dataset.classes]),
        ("student", [item.student_id for item in dataset.students]),
        ("question", [item.question_id for item in dataset.questions]),
        ("attempt", [item.attempt_id for item in dataset.attempts]),
        ("journey", [item.journey_id for item in dataset.journeys]),
    ):
        duplicate_ids = _duplicates(values)
        if duplicate_ids:
            errors.append(f"duplicate {label} IDs: {', '.join(duplicate_ids)}")

    for student in dataset.students:
        if student.class_id not in class_ids:
            errors.append(
                f"student {student.student_id} references unknown class {student.class_id}"
            )
    for question in dataset.questions:
        if question.skill_id not in graph_ids:
            errors.append(
                f"question {question.question_id} references unknown skill {question.skill_id}"
            )
    for item in dataset.attempts:
        if item.student_id not in student_ids:
            errors.append(
                f"attempt {item.attempt_id} references unknown student {item.student_id}"
            )
        if item.question_id not in question_ids:
            errors.append(
                f"attempt {item.attempt_id} references unknown question {item.question_id}"
            )
        if item.skill_id not in graph_ids:
            errors.append(
                f"attempt {item.attempt_id} references unknown skill {item.skill_id}"
            )
    for journey in dataset.journeys:
        if journey.student_id not in student_ids:
            errors.append(
                f"journey {journey.journey_id} references unknown student {journey.student_id}"
            )
        for attempt_id in journey.attempt_ids:
            if attempt_id not in attempt_ids:
                errors.append(
                    f"journey {journey.journey_id} references unknown attempt {attempt_id}"
                )

    canonical = dataset.model_dump_json().encode("utf-8")
    return SeedValidationReport(
        dataset_version=dataset.dataset_version,
        checksum=hashlib.sha256(canonical).hexdigest(),
        student_count=len(dataset.students),
        question_count=len(dataset.questions),
        attempt_count=len(dataset.attempts),
        journey_count=len(dataset.journeys),
        errors=tuple(errors),
    )


class InMemorySeedStore:
    def __init__(self) -> None:
        self._collections: dict[str, dict[str, BaseModel]] = {
            "classes": {},
            "students": {},
            "questions": {},
            "attempts": {},
            "journeys": {},
        }

    async def apply(self, dataset: MathPathSeed) -> dict[str, int]:
        report = validate_mathpath_seed(dataset)
        if report.errors:
            raise SeedConflict("; ".join(report.errors))
        batches = {
            "classes": (dataset.classes, "class_id"),
            "students": (dataset.students, "student_id"),
            "questions": (dataset.questions, "question_id"),
            "attempts": (dataset.attempts, "attempt_id"),
            "journeys": (dataset.journeys, "journey_id"),
        }
        created: dict[str, int] = {}
        for collection_name, (records, id_field) in batches.items():
            collection = self._collections[collection_name]
            count = 0
            for record in records:
                record_id = str(getattr(record, id_field))
                existing = collection.get(record_id)
                if existing is not None and existing != record:
                    raise SeedConflict(
                        f"{collection_name}/{record_id} conflicts with existing seed"
                    )
                if existing is None:
                    collection[record_id] = record
                    count += 1
            created[collection_name] = count
        return created

    def counts(self) -> dict[str, int]:
        return {
            name: len(collection)
            for name, collection in self._collections.items()
        }


def seed_manifest(dataset: MathPathSeed) -> dict[str, object]:
    report = validate_mathpath_seed(dataset)
    return {
        "dataset_version": report.dataset_version,
        "deterministic_seed": dataset.deterministic_seed,
        "graph_version": dataset.graph_version,
        "checksum": f"sha256:{report.checksum}",
        "counts": {
            "classes": len(dataset.classes),
            "students": report.student_count,
            "questions": report.question_count,
            "attempts": report.attempt_count,
            "journeys": report.journey_count,
        },
        "journey_ids": [journey.journey_id for journey in dataset.journeys],
        "privacy": {
            "pseudonymous": True,
            "forbidden_identity_fields": sorted(FORBIDDEN_STUDENT_IDENTITY_FIELDS),
        },
        "validation_errors": list(report.errors),
    }
