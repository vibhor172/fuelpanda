from app.custom_exceptions.base_exception import AppException


class ProductNotFound(AppException):
    code = "PRODUCT_NOT_FOUND"
    http_status = 404
    message = "Product not found"


class DuplicateProduct(AppException):
    code = "DUPLICATE_PRODUCT"
    http_status = 409
    message = "A product with this name or code already exists"
