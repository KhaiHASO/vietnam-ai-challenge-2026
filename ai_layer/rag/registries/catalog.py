from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

from ai_layer.config import settings

from .base import MissingCapabilityError, Registry
from .manifests import DomainManifest


class UnknownDomainError(LookupError):
    pass


@dataclass(frozen=True)
class ResolvedRequestContext:
    domain_id: str
    tenant_id: str
    manifest: DomainManifest
    versions: Mapping[str, str]
    adapters: Mapping[str, Any]


class RegistryCatalog:
    def __init__(
        self,
        *,
        domains: Mapping[str, DomainManifest] | None = None,
        registries: Mapping[str, Registry[Any]] | None = None,
        domains_root: str | Path | None = None,
    ) -> None:
        loaded_domains = dict(domains) if domains is not None else self._load_domains(
            Path(domains_root or settings.DOMAINS_ROOT)
        )
        self._domains: Mapping[str, DomainManifest] = MappingProxyType(loaded_domains)
        self._registries: Mapping[str, Registry[Any]] = MappingProxyType(
            dict(registries or {})
        )
        self._frozen = False

    @staticmethod
    def _load_domains(domains_root: Path) -> dict[str, DomainManifest]:
        loaded: dict[str, DomainManifest] = {}
        if not domains_root.exists():
            return loaded
        for domain_path in sorted(domains_root.iterdir()):
            manifest_path = domain_path / "domain.yaml"
            if domain_path.is_dir() and manifest_path.exists():
                data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                loaded[domain_path.name] = DomainManifest.model_validate(data)
        return loaded

    def freeze(self, *, readiness: bool = True) -> None:
        if self._frozen:
            return
        for registry in self._registries.values():
            registry.freeze(readiness=readiness)
        provider_registry = self._registries.get("provider")
        if provider_registry is not None:
            for domain_id, domain in self._domains.items():
                missing = [
                    provider_id
                    for provider_id in domain.provider_order
                    if not provider_registry.has(provider_id)
                ]
                if missing:
                    raise MissingCapabilityError(
                        f"Domain '{domain_id}' references missing providers: {', '.join(missing)}"
                    )
        self._frozen = True

    def resolve_request_context(
        self, domain_id: str, tenant_id: str
    ) -> ResolvedRequestContext:
        if not tenant_id.strip():
            raise ValueError("tenant_id cannot be blank")
        try:
            manifest = self._domains[domain_id]
        except KeyError as exc:
            raise UnknownDomainError(f"Unknown domain '{domain_id}'") from exc

        versions = {
            "domain_pack": manifest.version,
            "prompt": manifest.prompt_bundle_version,
            "policy": manifest.policy_bundle_version,
            "validator_bundle": manifest.validator_bundle_version,
        }
        adapters: dict[str, Any] = {}
        provider_registry = self._registries.get("provider")
        if provider_registry is not None:
            for provider_id in manifest.provider_order:
                if provider_registry.has(provider_id):
                    registration = provider_registry.registration(provider_id)
                    if domain_id in registration.manifest.supported_domains:
                        adapters["provider"] = registration.item
                        versions["provider"] = registration.manifest.version
                        break

        return ResolvedRequestContext(
            domain_id=domain_id,
            tenant_id=tenant_id,
            manifest=manifest,
            versions=MappingProxyType(versions),
            adapters=MappingProxyType(adapters),
        )
