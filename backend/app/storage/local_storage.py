import os
from pathlib import Path
from uuid import uuid4

from .object_storage import ObjectStorage


class LocalStorage(ObjectStorage):
    _TYPE_RULES = {
        "application/pdf": (".pdf", lambda data: data.startswith(b"%PDF-")),
        "image/png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
        "image/jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
            ".docx",
            lambda data: data.startswith(b"PK\x03\x04"),
        ),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": (
            ".xlsx",
            lambda data: data.startswith(b"PK\x03\x04"),
        ),
        "text/plain": (".txt", lambda data: b"\x00" not in data[:4096]),
        "text/csv": (".csv", lambda data: b"\x00" not in data[:4096]),
    }

    def __init__(self, root_dir: str | Path, *, max_bytes: int = 50 * 1024 * 1024):
        self.root_dir = Path(root_dir).resolve()
        self.quarantine_dir = self.root_dir / ".quarantine"
        self.max_bytes = max_bytes
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def store(self, original_filename: str, content: bytes, content_type: str) -> str:
        del original_filename
        if len(content) > self.max_bytes:
            raise ValueError("File too large")
        rule = self._TYPE_RULES.get(content_type)
        if rule is None:
            raise ValueError("Unsupported content type")
        extension, matches_magic = rule
        if not matches_magic(content):
            expected_for_other_type = any(
                matcher(content)
                for candidate_type, (_, matcher) in self._TYPE_RULES.items()
                if candidate_type != content_type
            )
            if expected_for_other_type:
                raise ValueError("Declared content type does not match file content")
            raise ValueError("File magic number is invalid")

        unique_name = f"uuid-{uuid4().hex}{extension}"
        quarantine_path = (self.quarantine_dir / f"{unique_name}.tmp").resolve()
        final_path = (self.root_dir / unique_name).resolve()
        self._assert_inside(quarantine_path, self.quarantine_dir)
        self._assert_inside(final_path, self.root_dir)
        with quarantine_path.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(quarantine_path, final_path)
        return unique_name

    def retrieve(self, path: str) -> bytes:
        full_path = (self.root_dir / path).resolve()
        self._assert_inside(full_path, self.root_dir)
        return full_path.read_bytes()

    @staticmethod
    def _assert_inside(path: Path, root: Path) -> None:
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("Invalid storage path") from exc
