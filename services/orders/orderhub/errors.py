"""Domain errors, mapped to HTTP status codes in api.py."""


class OrderHubError(Exception):
    status_code = 400


class NotFound(OrderHubError):
    status_code = 404


class Conflict(OrderHubError):
    status_code = 409


class ValidationFailed(OrderHubError):
    status_code = 422
