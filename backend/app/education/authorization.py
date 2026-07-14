from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException

from app.auth.contracts import Principal, Role

from .seed import MathPathSeed, SeedClass, SeedStudent, build_mathpath_seed


@lru_cache(maxsize=1)
def get_seed_directory() -> MathPathSeed:
    return build_mathpath_seed()


def forbidden() -> HTTPException:
    return HTTPException(status_code=403, detail="Insufficient permissions")


def not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Resource not found")


def require_education_role(principal: Principal, allowed: set[Role]) -> None:
    if principal.roles.isdisjoint(allowed):
        raise forbidden()


def require_seed_tenant(principal: Principal, seed: MathPathSeed) -> None:
    if principal.tenant_id != seed.tenant_id:
        raise not_found()


def class_by_id(seed: MathPathSeed, class_id: str) -> SeedClass:
    for item in seed.classes:
        if item.class_id == class_id:
            return item
    raise not_found()


def student_by_id(seed: MathPathSeed, student_id: str) -> SeedStudent:
    for item in seed.students:
        if item.student_id == student_id:
            return item
    raise not_found()


def can_read_class(principal: Principal, classroom: SeedClass) -> bool:
    if Role.ADMIN in principal.roles:
        return True
    if Role.TEACHER in principal.roles and principal.user_id == classroom.teacher_id:
        return True
    return False


def can_read_student(
    principal: Principal,
    *,
    student: SeedStudent,
    classroom: SeedClass,
) -> bool:
    if Role.ADMIN in principal.roles:
        return True
    if Role.TEACHER in principal.roles and principal.user_id == classroom.teacher_id:
        return True
    if Role.STUDENT in principal.roles and principal.user_id == student.student_id:
        return True
    return False
