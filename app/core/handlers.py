"""Convert domain errors to HTTP responses. This is the only place that maps errors to status codes."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    OperationNotAllowedError,
    TooManyAttemptsError,
    UnauthorizedError,
)

STATUS_CODES = {  # Error class -> HTTP status code
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    InvalidInputError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    OperationNotAllowedError: status.HTTP_405_METHOD_NOT_ALLOWED,
    TooManyAttemptsError: status.HTTP_429_TOO_MANY_REQUESTS,
}


def _status_for(error: AppError) -> int:
    for error_class, code in STATUS_CODES.items():
        if isinstance(error, error_class):
            return code
    return status.HTTP_400_BAD_REQUEST


def register_exception_handlers(app: FastAPI) -> None:  # Call one time when the app starts
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
        content = {"detail": error.message}
        if error.details:
            content["errors"] = error.details
        headers = {"WWW-Authenticate": "Bearer"} if isinstance(error, UnauthorizedError) else None
        return JSONResponse(status_code=_status_for(error), content=content, headers=headers)
