import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects a unique X-Request-ID and tracks request execution time.
    """
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # noqa: E501
        request_id = str(uuid.uuid4())

        # Bind the request_id to loguru context contextvars
        with logger.contextualize(request_id=request_id):
            start_time = time.time()
            client_host = request.client.host if request.client else "unknown"

            logger.info(f"Incoming Request: {request.method} {request.url.path} from {client_host}")  # noqa: E501

            try:
                response = await call_next(request)
            except Exception as e:
                process_time = (time.time() - start_time) * 1000
                logger.exception(f"Request Failed: {request.method} {request.url.path} - Runtime: {process_time:.2f}ms")  # noqa: E501
                raise e

            process_time = (time.time() - start_time) * 1000

            # Use custom log level / color formatting typically setup in loguru
            logger.info(f"Request Completed: {request.method} {request.url.path} - Status: {response.status_code} - Runtime: {process_time:.2f}ms")  # noqa: E501

            # Inject request ID into response for client traceability
            response.headers["X-Request-ID"] = request_id
            return response
