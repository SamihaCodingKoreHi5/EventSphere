import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("HTTPMiddleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        logger.info(
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Status: {response.status_code} | Duration: {process_time:.4f}s"
        )
        return response
