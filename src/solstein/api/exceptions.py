import sys
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


def setup_exception_handlers(app: FastAPI) -> None:
    """Register robust, structured global exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:  # noqa: E501
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Pydantic validation errors can be deeply nested. Format them clearly.
        errors = exc.errors()
        modified_details = [
            {"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")}
            for err in errors
        ]

        logger.warning(
            f"Aura | Validation Error [422] | {request.method} {request.url.path} | Details: {modified_details}"
        )  # noqa: E501

        return JSONResponse(
            status_code=422,
            content={
                "error": "Unprocessable Entity (Validation Error)",
                "details": modified_details,
                "request_id": request_id,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:  # noqa: E501
        request_id = getattr(request.state, "request_id", None) or "unknown"
        logger.warning(
            f"Aura | HTTP Exception [{exc.status_code}] | {request.method} {request.url.path} | Details: {exc.detail}"
        )  # noqa: E501

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "details": str(exc.detail),
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:  # noqa: E501
        """Catch-all for unhandled server errors (500). Captures full traceback."""
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Capture standard traceback for professional debugging
        exc_info = sys.exc_info()
        tb = (
            traceback.format_exception(*exc_info)
            if exc_info[0]
            else ["Unknown traceback"]
        )  # noqa: E501

        # logger.exception automatically captures context variables (like request_id)
        logger.exception(
            f"Aura | Unhandled Server Error [500] | {request.method} {request.url.path}"
        )  # noqa: E501

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc),
                "request_id": request_id,
                "traceback": tb,  # Exposed strictly for this deep-test QA audit environment  # noqa: E501
            },
        )
