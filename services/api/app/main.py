import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.queries import router as queries_router
from app.api.v1.scenes import router as scenes_router
from app.core.config import settings
from app.core.database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("framescout.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando FrameScout API...")
    # Em desenvolvimento local, inicializa as tabelas se necessário
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tabelas de banco verificadas.")
    yield
    logger.info("Encerrando FrameScout API...")
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="FrameScout Core API - Da narrativa à mídia com procedência e direitos.",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
    app.include_router(scenes_router, prefix=settings.API_V1_PREFIX)
    app.include_router(queries_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
