from app.custom_exceptions.base_exception import AppException


class VehicleAlreadyAllocated(AppException):
    code = "VEHICLE_ALREADY_ALLOCATED"
    http_status = 409
    message = "Vehicle is already allocated for this date"


class AllocationNotFound(AppException):
    code = "ALLOCATION_NOT_FOUND"
    http_status = 404
    message = "Allocation not found"


class AllocationConflict(AppException):
    code = "ALLOCATION_CONFLICT"
    http_status = 409
    message = "Allocation cannot be modified in its current state"
