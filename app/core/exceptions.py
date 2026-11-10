"""Domain errors. Services raise these. They do not know about HTTP.

app/core/handlers.py converts each error to an HTTP response.
"""


class AppError(Exception):  # Base class for all errors that the API shows to the client
    def __init__(self, message: str, details: dict | list | None = None):
        super().__init__(message)
        self.message = message  # Text for the client
        self.details = details  # More data, for example the fields that failed


class UnauthorizedError(AppError):  # No valid login, or the token is not valid
    pass


class ForbiddenError(AppError):  # The user is logged in but does not have the privilege
    pass


class NotFoundError(AppError):  # The record does not exist
    pass


class ConflictError(AppError):  # The change breaks a rule about the data that is stored
    pass


class InvalidInputError(AppError):  # The input breaks a business rule
    pass


class TooManyAttemptsError(AppError):  # Too many failed attempts, for example failed logins
    pass


class OperationNotAllowedError(AppError):  # The resource does not support the operation
    pass
