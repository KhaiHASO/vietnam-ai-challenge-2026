from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Generic, TypeVar

from .manifests import CapabilityManifest

T = TypeVar("T")


class RegistryError(RuntimeError):
    pass


class DuplicateRegistrationError(RegistryError):
    pass


class FrozenRegistryError(RegistryError):
    pass


class MissingCapabilityError(RegistryError):
    pass


class ConfigSchemaError(RegistryError):
    pass


class UnhealthyCapabilityError(RegistryError):
    pass


@dataclass(frozen=True)
class Registration(Generic[T]):
    manifest: CapabilityManifest
    item: T
    config: Mapping[str, Any]
    healthcheck: Callable[[], bool] | None


class Registry(Generic[T]):
    def __init__(self, name: str):
        self.name = name
        self._registrations: dict[tuple[str, str], Registration[T]] = {}
        self._frozen = False
        self._items: Mapping[tuple[str, str], Registration[T]] = self._registrations

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def registrations(self) -> Mapping[tuple[str, str], Registration[T]]:
        return self._items

    def register(
        self,
        manifest: CapabilityManifest,
        item: T,
        *,
        config: Mapping[str, Any] | None = None,
        healthcheck: Callable[[], bool] | None = None,
    ) -> None:
        if self._frozen:
            raise FrozenRegistryError(
                f"Cannot register '{manifest.id}' - {self.name} registry is frozen"
            )
        key = (manifest.id, manifest.version)
        if key in self._registrations:
            raise DuplicateRegistrationError(
                f"Item '{manifest.id}@{manifest.version}' is already registered in {self.name}"
            )
        self._registrations[key] = Registration(
            manifest=manifest,
            item=item,
            config=MappingProxyType(dict(config or {})),
            healthcheck=healthcheck,
        )

    def freeze(self, *, readiness: bool = True) -> None:
        if self._frozen:
            return
        for registration in self._registrations.values():
            self._validate_config(registration)
            if readiness and registration.manifest.required:
                if registration.healthcheck is None or not self._healthcheck_passed(
                    registration.healthcheck
                ):
                    manifest = registration.manifest
                    raise UnhealthyCapabilityError(
                        f"Required {self.name} '{manifest.id}@{manifest.version}' is unhealthy"
                    )
        self._items = MappingProxyType(dict(self._registrations))
        self._frozen = True

    @staticmethod
    def _healthcheck_passed(healthcheck: Callable[[], bool]) -> bool:
        try:
            return bool(healthcheck())
        except Exception:
            return False

    def _validate_config(self, registration: Registration[T]) -> None:
        schema = registration.manifest.config_schema
        config = registration.config
        missing = [key for key in schema.get("required", []) if key not in config]
        if missing:
            raise ConfigSchemaError(
                f"{self.name} '{registration.manifest.id}' is missing config: {', '.join(missing)}"
            )
        properties = schema.get("properties", {})
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": Mapping,
            "array": (list, tuple),
        }
        for key, value in config.items():
            expected_name = properties.get(key, {}).get("type")
            expected = type_map.get(expected_name)
            if expected and not isinstance(value, expected):
                raise ConfigSchemaError(
                    f"{self.name} '{registration.manifest.id}' config '{key}' must be {expected_name}"
                )

    def versions_for(self, capability_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(version for item_id, version in self._items if item_id == capability_id)
        )

    def has(self, capability_id: str, version: str | None = None) -> bool:
        if version is not None:
            return (capability_id, version) in self._items
        return any(item_id == capability_id for item_id, _ in self._items)

    def get(self, capability_id: str, version: str | None = None) -> T:
        registration = self.registration(capability_id, version)
        return registration.item

    def registration(
        self, capability_id: str, version: str | None = None
    ) -> Registration[T]:
        selected_version = version
        if selected_version is None:
            versions = self.versions_for(capability_id)
            if not versions:
                raise MissingCapabilityError(
                    f"Unknown {self.name} capability '{capability_id}'"
                )
            selected_version = versions[-1]
        try:
            return self._items[(capability_id, selected_version)]
        except KeyError as exc:
            raise MissingCapabilityError(
                f"Unknown {self.name} capability '{capability_id}@{selected_version}'"
            ) from exc
