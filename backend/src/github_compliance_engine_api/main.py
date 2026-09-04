from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from github_compliance_engine_api.api.routes import router
from github_compliance_engine_api.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="GitHub Compliance Engine API",
        version="0.1.0",
        description="Analysis API scaffold for Golden Thread repo compliance.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
