from app.custom_exceptions.base_exception import AppException


class InventoryNotFound(AppException):
    code = "INVENTORY_NOT_FOUND"
    http_status = 404
    message = "Inventory record not found"


class NegativeQuantity(AppException):
    code = "NEGATIVE_QUANTITY"
    http_status = 422
    message = "Inventory quantity cannot be negative"
