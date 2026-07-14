import pytest

from ai_layer.rag.registries.base import (
    ConfigSchemaError,
    Registry,
    DuplicateRegistrationError,
    FrozenRegistryError,
    UnhealthyCapabilityError,
)
from ai_layer.rag.registries.manifests import CapabilityManifest

def test_registry_rejects_duplicate_id_and_version() -> None:
    registry = Registry[object]("provider")
    manifest = CapabilityManifest(
        id="deepseek", 
        version="1.0.0", 
        capabilities=[], 
        supported_domains=["agriculture"], 
        config_schema={}, 
        risk_class="low"
    )
    registry.register(manifest, object())
    with pytest.raises(DuplicateRegistrationError):
        registry.register(manifest, object())

def test_registry_cannot_mutate_after_freeze() -> None:
    registry = Registry[object]("provider")
    registry.freeze()
    manifest = CapabilityManifest(
        id="ollama", 
        version="1.0.0", 
        capabilities=[], 
        supported_domains=["agriculture"], 
        config_schema={}, 
        risk_class="low"
    )
    with pytest.raises(FrozenRegistryError):
        registry.register(manifest, object())


def test_registry_supports_multiple_versions_of_the_same_capability() -> None:
    registry = Registry[object]("provider")
    first = CapabilityManifest(
        id="deepseek", version="1.0.0", capabilities=["chat"],
        supported_domains=["agriculture"], config_schema={}, risk_class="low"
    )
    second = first.model_copy(update={"version": "2.0.0"})
    v1, v2 = object(), object()
    registry.register(first, v1)
    registry.register(second, v2)
    registry.freeze()
    assert registry.get("deepseek", "1.0.0") is v1
    assert registry.get("deepseek", "2.0.0") is v2


def test_registry_freeze_fails_for_invalid_config() -> None:
    registry = Registry[object]("provider")
    manifest = CapabilityManifest(
        id="deepseek", version="1", capabilities=["chat"],
        supported_domains=["agriculture"],
        config_schema={"required": ["api_key"]}, risk_class="low"
    )
    registry.register(manifest, object(), config={})
    with pytest.raises(ConfigSchemaError):
        registry.freeze()


def test_registry_freeze_fails_for_unhealthy_required_capability() -> None:
    registry = Registry[object]("provider")
    manifest = CapabilityManifest(
        id="deepseek", version="1", capabilities=["chat"],
        supported_domains=["agriculture"], config_schema={}, risk_class="low",
        required=True,
    )
    registry.register(manifest, object(), healthcheck=lambda: False)
    with pytest.raises(UnhealthyCapabilityError):
        registry.freeze(readiness=True)
