from app.custom_exceptions.base_exception import AppException


class VehicleNotFound(AppException):
    code = "VEHICLE_NOT_FOUND"
    http_status = 404
    message = "Vehicle not found"


class VehicleUnavailable(AppException):
    code = "VEHICLE_UNAVAILABLE"
    http_status = 409
    message = "Vehicle is not available for allocation"


class DuplicateVehicleRegistration(AppException):
    code = "DUPLICATE_VEHICLE_REGISTRATION"
    http_status = 409
    message = "A vehicle with this registration number already exists"
