from app.custom_exceptions.base_exception import AppException


class ShiftNotFound(AppException):
    code = "SHIFT_NOT_FOUND"
    http_status = 404
    message = "Shift not found"


class NoAllocationForShift(AppException):
    code = "NO_ALLOCATION_FOR_SHIFT"
    http_status = 409
    message = "No active vehicle allocation exists for this shift"


class ShiftAlreadyActive(AppException):
    code = "SHIFT_ALREADY_ACTIVE"
    http_status = 409
    message = "Shift is already active"


class ShiftNotActive(AppException):
    code = "SHIFT_NOT_ACTIVE"
    http_status = 409
    message = "Shift is not active"


class InvalidShiftTransition(AppException):
    code = "INVALID_SHIFT_TRANSITION"
    http_status = 409
    message = "Invalid shift state transition"
