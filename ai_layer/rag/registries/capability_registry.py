import os
from typing import Dict, Any
from ai_layer.config import settings


CAPABILITIES: Dict[str, Dict[str, Any]] = {}


def load_capabilities():
    global CAPABILITIES
    domain_dir = settings.domain_dir
    if not os.path.isdir(domain_dir):
        return
    for name in os.listdir(domain_dir):
        pack_path = os.path.join(domain_dir, name)
        if os.path.isdir(pack_path):
            CAPABILITIES[name] = {"name": name, "path": pack_path}


load_capabilities()


def get_capability(domain: str) -> Dict[str, Any]:
    if not domain or domain == "default":
        return {}
    if domain in CAPABILITIES:
        return CAPABILITIES[domain]
    root = settings.domain_dir
    if root and os.path.isdir(root):
        candidate = os.path.join(root, domain)
        if os.path.isdir(candidate):
            CAPABILITIES[domain] = {"name": domain, "path": candidate}
            return CAPABILITIES[domain]
    return {}


def get_capability_registry():
    return {"get_capability": get_capability, "capabilities": CAPABILITIES}
