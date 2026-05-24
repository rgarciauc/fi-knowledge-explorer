from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import configure_logging

configure_logging()

from .db import close_driver, verify_connectivity  # noqa: E402
from .routes import router  # noqa: E402


logger = logging.getLogger("super_bank.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application.starting")
    try:
        verify_connectivity()
        logger.info("application.neo4j_ready")
    except Exception:
        logger.exception("application.startup_failed dependency=neo4j")
        raise
    yield
    logger.info("application.stopping")
    close_driver()


app = FastAPI(title="SUPER_BANK Knowledge Graph API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    started = perf_counter()

    logger.info(
        "http.request_started request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )
    response = await call_next(request)
    duration_ms = round((perf_counter() - started) * 1000)
    response.headers["x-request-id"] = request_id
    logger.info(
        "http.request_completed request_id=%s method=%s path=%s status=%d duration_ms=%d",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "not-assigned")
    logger.error(
        "http.unhandled_error request_id=%s method=%s path=%s error=%s",
        request_id,
        request.method,
        request.url.path,
        str(exc),
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Backend processing failed. Inspect backend.log using the request ID.",
            "request_id": request_id,
        },
        headers={"x-request-id": request_id},
    )


@app.get("/health")
def health() -> dict[str, str]:
    try:
        verify_connectivity()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Neo4j is unavailable") from exc
    return {"status": "ok", "neo4j": "available"}
