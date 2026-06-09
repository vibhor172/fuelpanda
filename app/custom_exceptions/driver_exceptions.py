from app.custom_exceptions.base_exception import AppException


class DriverNotFound(AppException):
    code = "DRIVER_NOT_FOUND"
    http_status = 404
    message = "Driver not found"


class DriverInactive(AppException):
    code = "DRIVER_INACTIVE"
    http_status = 409
    message = "Driver is not active"


class DuplicateDriverLicense(AppException):
    code = "DUPLICATE_DRIVER_LICENSE"
    http_status = 409
    message = "A driver with this license number already exists"
