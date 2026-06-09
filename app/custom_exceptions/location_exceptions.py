from app.custom_exceptions.base_exception import AppException


class LocationNotFound(AppException):
    code = "LOCATION_NOT_FOUND"
    http_status = 404
    message = "Location not found"
