import logging

import pymysql
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database_api.errors import AppError, translate_mysql_error
from routes import routers

log = logging.getLogger("tower_running")

app = FastAPI(title="Tower Running")

for router in routers:
    app.include_router(router)


# Every error response has the shape {"detail": "<readable message>"}.

@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    # Validation (400), not found (404), conflict (409), DB down (503)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(pymysql.err.MySQLError)
def handle_mysql_error(request: Request, exc: pymysql.err.MySQLError):
    # Safety net for any MySQL error raised outside _Database.execute
    err = translate_mysql_error(exc)
    return JSONResponse(status_code=err.status_code, content={"detail": err.message})


@app.exception_handler(RequestValidationError)
def handle_request_validation(request: Request, exc: RequestValidationError):
    # Pydantic/FastAPI input errors (wrong type, missing field) as one message
    problems = []
    for e in exc.errors():
        field = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
        problems.append(f"{field}: {e['msg']}" if field else e["msg"])
    return JSONResponse(status_code=422, content={"detail": "; ".join(problems)})


@app.exception_handler(Exception)
def handle_unexpected(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
