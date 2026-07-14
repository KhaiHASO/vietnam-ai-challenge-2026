import pytest
import re
from pathlib import Path

from ai_layer.rag.registries.base import MissingCapabilityError, Registry
from ai_layer.rag.registries.catalog import RegistryCatalog
from ai_layer.rag.registries.manifests import CapabilityManifest, DomainManifest
from ai_layer.rag.registries.capability_registry import get_capability

def test_catalog_resolve_domain() -> None:
    catalog = RegistryCatalog()
    # Assuming domains_root is set and agriculture domain exists
    context = catalog.resolve_request_context("agriculture", "tenant_1")
    assert context.tenant_id == "tenant_1"
    assert context.manifest.version == "1.0.0"
    assert context.manifest.locale == "vi-VN"
    assert context.manifest.max_reflect_count == 2


def test_catalog_freeze_rejects_a_domain_provider_reference_that_is_missing() -> None:
    provider_registry = Registry[object]("provider")
    domain = DomainManifest(
        version="1.0.0", locale="vi-VN", prompt_bundle_version="p1",
        policy_bundle_version="policy1", validator_bundle_version="v1",
        memory_policy={"allowed_fact_fields": []},
        retrieval={"similarity_threshold": 0.7, "top_k": 3},
        provider_order=["missing-provider"], max_reflect_count=2,
        tool_risk_classes=[],
    )
    catalog = RegistryCatalog(
        domains={"agriculture": domain}, registries={"provider": provider_registry}
    )
    with pytest.raises(MissingCapabilityError):
        catalog.freeze(readiness=False)


def test_legacy_capability_shim_delegates_without_mutating_global_domain() -> None:
    with pytest.deprecated_call():
        capability = get_capability("agriculture", tenant_id="tenant-a")
    assert capability["domain_id"] == "agriculture"
    assert capability["tenant_id"] == "tenant-a"
    assert capability["version"] == "1.0.0"


def test_production_code_has_no_mutable_global_domain_configuration() -> None:
    project_root = Path(__file__).resolve().parents[4]
    offenders: list[str] = []
    forbidden = re.compile(
        r"ACTIVE_DOMAIN|settings\.domain_dir\b|settings\.db_path\b|settings\.vector_db_path\b"
    )
    for source_root in (project_root / "ai_layer", project_root / "backend" / "app"):
        for path in source_root.rglob("*.py"):
            content = path.read_text(encoding="utf-8-sig")
            if forbidden.search(content):
                offenders.append(str(path.relative_to(project_root)))

    assert offenders == []
