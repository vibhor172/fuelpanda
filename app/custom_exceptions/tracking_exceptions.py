from app.custom_exceptions.base_exception import AppException


class NoActiveShiftForGps(AppException):
    code = "NO_ACTIVE_SHIFT_FOR_GPS"
    http_status = 409
    message = "GPS updates are only accepted during an active shift"


class InvalidCoordinates(AppException):
    code = "INVALID_COORDINATES"
    http_status = 422
    message = "Coordinates are out of range"
