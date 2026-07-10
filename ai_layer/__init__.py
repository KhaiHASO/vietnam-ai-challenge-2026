def __getattr__(name):
    if name == "AIOrchestrator":
        from ai_layer.orchestrator import AIOrchestrator
        return AIOrchestrator
    if name == "hitl_manager":
        from ai_layer.approval.hitl import hitl_manager
        return hitl_manager
    if name in ("load_db", "save_db"):
        from ai_layer.tools.db_mock import load_db, save_db
        return load_db if name == "load_db" else save_db
    raise AttributeError(f"module 'ai_layer' has no attribute {name!r}")
