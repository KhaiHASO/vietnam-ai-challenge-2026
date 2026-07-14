import pytest
import os
import tempfile
import shutil
from backend.app.storage.local_storage import LocalStorage

def test_local_storage_atomic_rename():
    path = tempfile.mkdtemp()
    try:
        storage = LocalStorage(path)
        content = b"%PDF-1.7\ncontent"
        stored = storage.store("test.pdf", content, "application/pdf")
        
        assert stored.startswith("uuid-")
        assert stored.endswith(".pdf")
        
        retrieved = storage.retrieve(stored)
        assert retrieved == content
    finally:
        shutil.rmtree(path, ignore_errors=True)

def test_local_storage_path_traversal_prevention():
    path = tempfile.mkdtemp()
    try:
        storage = LocalStorage(path)
        with pytest.raises(ValueError):
            storage.retrieve("../../../../etc/passwd")
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_local_storage_rejects_mime_spoofing() -> None:
    path = tempfile.mkdtemp()
    try:
        storage = LocalStorage(path)
        with pytest.raises(ValueError, match="content|magic number"):
            storage.store("report.pdf", b"plain text", "application/pdf")
        with pytest.raises(ValueError, match="content type"):
            storage.store("report.pdf", b"%PDF-1.7\n", "image/png")
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_local_storage_rejects_sibling_prefix_escape() -> None:
    parent = tempfile.mkdtemp()
    root = os.path.join(parent, "store")
    sibling = os.path.join(parent, "store-evil")
    os.makedirs(sibling)
    try:
        storage = LocalStorage(root)
        with pytest.raises(ValueError):
            storage.retrieve("../store-evil/secret.pdf")
    finally:
        shutil.rmtree(parent, ignore_errors=True)
