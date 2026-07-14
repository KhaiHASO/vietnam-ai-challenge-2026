import logging
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
# Load root .env file
root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(root_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_layer.cropdoctor.api.router import router as cropdoctor_router

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.db.mongo import close_mongo_connection, connect_to_mongo
from app.db.mongo import mongo_state
from app.db.redis import close_redis_connection, connect_to_redis
from app.routes import (
    ai,
    approvals,
    chat,
    cooperative,
    dashboard,
    database,
    diagnosis,
    domain,
    expert,
    health,
    knowledge,
    listing,
    status,
)
from app.auth.routes import admin_router, router as auth_router
from app.services.startup_service import initialize_demo_state

logger = logging.getLogger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.demo_mode:
        try:
            initialize_demo_state()
        except Exception:
            logger.exception("Demo data initialization failed")

    await connect_to_mongo()
    redis_client = await connect_to_redis()
    app.state.redis = redis_client
    if settings.environment == "production" and (
        not mongo_state.connected or redis_client is None
    ):
        await close_redis_connection()
        await close_mongo_connection()
        raise RuntimeError("MongoDB and Redis are required in production")

    if mongo_state.connected:
        from app.auth.bootstrap import bootstrap_first_admin
        from app.auth.repository import AuthRepository

        await bootstrap_first_admin(
            AuthRepository(),
            username=settings.bootstrap_admin_username,
            password=(
                settings.bootstrap_admin_password.get_secret_value()
                if settings.bootstrap_admin_password
                else None
            ),
            tenant_id=settings.bootstrap_admin_tenant_id,
        )
    try:
        yield
    finally:
        await close_redis_connection()
        await close_mongo_connection()


from app.middleware.request_context import RequestContextMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from app.middleware.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)




    # Only diagnosis images are public assets. Knowledge source documents remain private.
    diagnosis_upload_path = settings.upload_root_path / "diagnosis_cases"
    os.makedirs(diagnosis_upload_path, exist_ok=True)
    app.mount(
        "/uploads/diagnosis_cases",
        StaticFiles(directory=str(diagnosis_upload_path)),
        name="diagnosis_uploads",
    )

    from fastapi import Depends
    from app.auth.dependencies import get_current_user
    auth_dep = [Depends(get_current_user)]

    app.include_router(health.router)
    app.include_router(status.router, dependencies=auth_dep)
    
    app.include_router(ai.router, dependencies=auth_dep)
    app.include_router(domain.router, dependencies=auth_dep)
    app.include_router(diagnosis.router, dependencies=auth_dep)
    app.include_router(expert.router, dependencies=auth_dep)
    app.include_router(dashboard.router, dependencies=auth_dep)
    app.include_router(listing.router, dependencies=auth_dep)
    app.include_router(knowledge.router, dependencies=auth_dep)
    app.include_router(cooperative.router, dependencies=auth_dep)

    app.include_router(chat.router, dependencies=auth_dep)
    app.include_router(database.router, dependencies=auth_dep)
    app.include_router(approvals.router, dependencies=auth_dep)
    app.include_router(cropdoctor_router, dependencies=auth_dep)
    
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1", dependencies=auth_dep)

    from app.copilot.routes import router as copilot_router
    from app.copilot.memory_routes import router as memory_router
    from app.knowledge.routes import router as knowledge_ingestion_router
    from app.observability.routes import router as observability_router
    app.include_router(copilot_router, dependencies=auth_dep)
    app.include_router(memory_router, dependencies=auth_dep)
    app.include_router(knowledge_ingestion_router)
    app.include_router(observability_router)

    return app

app = create_app()
