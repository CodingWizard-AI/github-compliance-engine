from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.include_router(router)
    return app


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": [_safe_validation_error(error) for error in exc.errors()]},
    )


def _safe_validation_error(error: dict[str, Any]) -> dict[str, Any]:
    safe_error = {key: value for key, value in error.items() if key not in {"input", "ctx"}}
    safe_ctx = _safe_validation_context(error.get("ctx"))
    if safe_ctx:
        safe_error["ctx"] = safe_ctx
    return safe_error


def _safe_validation_context(ctx: Any) -> dict[str, Any] | None:
    if not isinstance(ctx, dict):
        return None
    safe_ctx = {
        key: value
        for key, value in ctx.items()
        if key != "error" and isinstance(value, str | int | float | bool | type(None))
    }
    return safe_ctx or None


app = create_app()
