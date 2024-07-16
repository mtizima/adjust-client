class AdjustClientError(Exception):
    """Base class for other exceptions"""
    pass


class BadEventStateError(AdjustClientError):
    pass


class AuthorizationError(AdjustClientError):
    pass


class AppInactiveError(AdjustClientError):
    pass


class TrackingDisabledError(AdjustClientError):
    pass


class EventTokenBlocklistedError(AdjustClientError):
    pass


class AppTokenNotFoundError(AdjustClientError):
    pass


class DeviceNotFoundError(AdjustClientError):
    pass


class RequestSizeTooLargeError(AdjustClientError):
    pass


class DeviceOptedOutError(AdjustClientError):
    pass


class InternalServerError(AdjustClientError):
    pass
