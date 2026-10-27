"""Application errors. Services raise these; the error handler turns them into
the standard JSON envelope with the matching HTTP status."""


class AppError(Exception):
    status_code = 500
    default_message = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    default_message = "Bad request"


class UnauthorizedError(AppError):
    status_code = 401
    default_message = "Authentication required"


class ForbiddenError(AppError):
    status_code = 403
    default_message = "You do not have access to this resource"


class NotFoundError(AppError):
    status_code = 404
    default_message = "Not found"


class ConflictError(AppError):
    status_code = 409
    default_message = "Already exists"
