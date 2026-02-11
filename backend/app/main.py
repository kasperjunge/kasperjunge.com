import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analytics import router as analytics_router
from app.api.v1.contact import router as contact_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.core.request_meta import extract_client_ip

request_logger = logging.getLogger("app.request")


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings)
    docs_url = "/docs" if settings.docs_enabled else None
    redoc_url = "/redoc" if settings.docs_enabled else None
    openapi_url = "/openapi.json" if settings.docs_enabled else None
    app = FastAPI(
        title="Kasper Junge Backend",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(contact_router)
    app.include_router(analytics_router)

    @app.middleware("http")
    async def log_request_metrics(request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        request_logger.info(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": extract_client_ip(request),
            },
        )

        return response

    return app


app = create_app()
