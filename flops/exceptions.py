class ApiError(Exception):
    pass


class AuthError(ApiError):
    pass


class ApiLimitError(ApiError):
    pass


class NotFoundError(ApiError):
    pass


class ValidationError(ApiError):
    pass


class OperationError(ApiError):
    pass


class OperationTimeoutError(ApiError):
    pass
