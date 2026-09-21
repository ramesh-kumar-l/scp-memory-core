"""Domain-level service errors, mapped to HTTP problem responses in the API."""


class ServiceError(Exception):
    """Base class for service-layer errors."""

    code = "error"


class NotFoundError(ServiceError):
    """Requested memory does not exist (or is out of the caller's namespace)."""

    code = "not_found"
