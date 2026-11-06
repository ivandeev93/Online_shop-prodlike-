class ProductNotFoundError(Exception):
    def __init__(self, message: str = "Product not found"):
        super().__init__(message)


class ProductPermissionDeniedError(Exception):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)
