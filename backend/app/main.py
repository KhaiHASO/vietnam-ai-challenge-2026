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
    yield
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
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    # Mount static files for images serving
    os.makedirs(settings.upload_root_path, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_root_path)), name="uploads")
    os.makedirs("tmp_uploads", exist_ok=True)
    app.mount("/tmp_uploads", StaticFiles(directory="tmp_uploads"), name="tmp_uploads")

    app.include_router(health.router)
    app.include_router(status.router)
    app.include_router(ai.router)
    app.include_router(domain.router)
    app.include_router(diagnosis.router)
    app.include_router(expert.router)
    app.include_router(dashboard.router)
    app.include_router(listing.router)
    app.include_router(knowledge.router)
    app.include_router(cooperative.router)

    app.include_router(chat.router)
    app.include_router(database.router)
    app.include_router(approvals.router)
    app.include_router(cropdoctor_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")

    from app.copilot.routes import router as copilot_router
    from app.copilot.memory_routes import router as memory_router
    app.include_router(copilot_router)
    app.include_router(memory_router)

    return app

app = create_app()
