import logging
from pathlib import Path

import pymysql
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from database_api.errors import AppError, translate_mysql_error
from routes import routers
from routes.pages import render, router as pages_router

log = logging.getLogger("tower_running")
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Tower Running")

# JSON API (used by the forms and buttons on the pages): /api/...
for router in routers:
    app.include_router(router, prefix="/api")

# Server-rendered pages: /, /races, /ranking, /members, /news, ...
app.include_router(pages_router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def _error(request: Request, status_code: int, message: str):
    """JSON {"detail": ...} for the API, a normal site page for everything else."""
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status_code, content={"detail": message})
    return render(request, "error.html", status_code=status_code, message=message, title="Error")


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    # Validation (400), not found (404), conflict (409), DB down (503)
    return _error(request, exc.status_code, exc.message)


@app.exception_handler(pymysql.err.MySQLError)
def handle_mysql_error(request: Request, exc: pymysql.err.MySQLError):
    # Safety net for any MySQL error raised outside _Database.execute
    err = translate_mysql_error(exc)
    return _error(request, err.status_code, err.message)


@app.exception_handler(RequestValidationError)
def handle_request_validation(request: Request, exc: RequestValidationError):
    # Pydantic/FastAPI input errors (wrong type, missing field) as one message
    problems = []
    for e in exc.errors():
        field = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
        problems.append(f"{field}: {e['msg']}" if field else e["msg"])
    return _error(request, 422, "; ".join(problems))


@app.exception_handler(StarletteHTTPException)
def handle_http_error(request: Request, exc: StarletteHTTPException):
    # Unknown URL (404), wrong method (405), ...
    message = "Page not found" if exc.status_code == 404 else str(exc.detail)
    return _error(request, exc.status_code, message)


@app.exception_handler(Exception)
def handle_unexpected(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _error(request, 500, "Internal server error")
