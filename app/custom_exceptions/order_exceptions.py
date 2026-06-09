from app.custom_exceptions.base_exception import AppException


class OrderNotFound(AppException):
    code = "ORDER_NOT_FOUND"
    http_status = 404
    message = "Order not found"


class InvalidOrderStatus(AppException):
    code = "INVALID_ORDER_STATUS"
    http_status = 409
    message = "Order is not in a valid state for this operation"


class DeliveryAlreadyFinalized(AppException):
    code = "DELIVERY_ALREADY_FINALIZED"
    http_status = 409
    message = "Delivery has already been completed or failed"


class MissingFailureReason(AppException):
    code = "MISSING_FAILURE_REASON"
    http_status = 422
    message = "A failure reason is required to fail a delivery"
