import warnings
from functools import lru_cache
from typing import Any

from .catalog import RegistryCatalog


@lru_cache(maxsize=1)
def _catalog() -> RegistryCatalog:
    catalog = RegistryCatalog()
    catalog.freeze(readiness=False)
    return catalog


def load_capabilities() -> RegistryCatalog:
    warnings.warn(
        "load_capabilities is deprecated. Use RegistryCatalog instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _catalog()


def get_capability(domain: str, tenant_id: str = "single") -> dict[str, Any]:
    warnings.warn(
        "get_capability is deprecated. Use RegistryCatalog instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    context = _catalog().resolve_request_context(domain, tenant_id)
    return {
        "domain_id": context.domain_id,
        "tenant_id": context.tenant_id,
        **context.manifest.model_dump(),
    }


def get_capability_registry() -> dict[str, Any]:
    warnings.warn(
        "get_capability_registry is deprecated. Use RegistryCatalog instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return {"get_capability": get_capability, "catalog": _catalog()}
