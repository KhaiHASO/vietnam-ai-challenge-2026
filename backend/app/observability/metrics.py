from __future__ import annotations

import re
from collections import defaultdict
from typing import Mapping


_METRIC = re.compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$")
_LABEL = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class MetricRegistry:
    def __init__(self) -> None:
        self._values: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)

    def record(self, name: str, value: float = 1, *, labels: Mapping[str, str] | None = None) -> None:
        if not _METRIC.fullmatch(name):
            raise ValueError("Invalid metric name")
        normalized = tuple(sorted((key, str(label)) for key, label in (labels or {}).items() if _LABEL.fullmatch(key)))
        self._values[(name, normalized)] += value

    def render(self) -> str:
        lines: list[str] = []
        for (name, labels), value in sorted(self._values.items()):
            suffix = "" if not labels else "{" + ",".join(f'{key}="{label.replace(chr(34), chr(92) + chr(34))}"' for key, label in labels) + "}"
            lines.append(f"{name}{suffix} {value}")
        return "\n".join(lines) + ("\n" if lines else "")


metrics = MetricRegistry()
