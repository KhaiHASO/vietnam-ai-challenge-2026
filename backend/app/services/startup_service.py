import logging

from ai_layer.rag.knowledge_base import seed_knowledge_base
from ai_layer.tools.db_mock import load_db

logger = logging.getLogger("backend.startup")


def initialize_demo_state() -> None:
    logger.info("Initializing demo data for domain '%s'", "agriculture")
    seed_knowledge_base()
    load_db("agriculture")
