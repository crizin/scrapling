from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import dynamic, fetch, stealth

logger = logging.getLogger("scrapling-api")

_semaphore: asyncio.Semaphore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _semaphore
    _semaphore = asyncio.Semaphore(settings.api_max_concurrent)
    yield


app = FastAPI(title="Scrapling API", version="1.0.0", lifespan=lifespan)


# --- Middleware: API key authentication ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if settings.api_key and request.url.path != "/health":
        api_key = request.headers.get("X-API-Key", "")
        if api_key != settings.api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


# --- Middleware: concurrency limiter ---
@app.middleware("http")
async def concurrency_middleware(request: Request, call_next):
    if request.url.path in ("/dynamic", "/stealth"):
        assert _semaphore is not None
        if _semaphore.locked() and _semaphore._value == 0:
            return JSONResponse(status_code=429, content={"detail": "Too many concurrent browser requests"})
        async with _semaphore:
            return await call_next(request)
    return await call_next(request)


# --- Middleware: hard timeout ---
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    if request.url.path in ("/fetch", "/dynamic", "/stealth"):
        max_timeout = (
            settings.api_stealth_timeout_max
            if request.url.path == "/stealth"
            else settings.api_timeout_max
        )
        try:
            return await asyncio.wait_for(call_next(request), timeout=max_timeout + 5)
        except asyncio.TimeoutError:
            return JSONResponse(status_code=504, content={"detail": "Request timed out"})
    return await call_next(request)


# --- Exception handlers ---
@app.exception_handler(ConnectionError)
async def connection_error_handler(request: Request, exc: ConnectionError):
    return JSONResponse(status_code=502, content={"detail": f"Connection failed: {exc}"})


@app.exception_handler(TimeoutError)
async def timeout_error_handler(request: Request, exc: TimeoutError):
    return JSONResponse(status_code=504, content={"detail": f"Upstream timeout: {exc}"})


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# --- Health check ---
@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Register routers ---
app.include_router(fetch.router)
app.include_router(dynamic.router)
app.include_router(stealth.router)
