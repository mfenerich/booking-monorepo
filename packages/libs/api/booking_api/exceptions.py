"""API exception handling utilities."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .responses import ErrorResponse


class APIError(Exception):
    """Base class for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = None,
        details: dict = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            **kwargs
        )


class ConflictError(APIError):
    """Conflict error, e.g., duplicate resource."""

    def __init__(self, message: str = "Resource already exists", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            **kwargs
        )


class UnauthorizedError(APIError):
    """Unauthorized error."""

    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            **kwargs
        )


class ForbiddenError(APIError):
    """Forbidden error."""

    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            **kwargs
        )


class BadRequestError(APIError):
    """Bad request error."""

    def __init__(self, message: str = "Bad request", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            **kwargs
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handler for API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message, error_code=exc.error_code, details=exc.details
        ).model_dump(),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


def configure_exception_handlers(app):
    """Configure exception handlers for a FastAPI application."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    return app
