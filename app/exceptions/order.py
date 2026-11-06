class CartIsEmptyError(Exception):
    def __init__(self, message: str = "Cart is empty"):
        super().__init__(message)


class OrderNotFoundError(Exception):
    def __init__(self, message: str = "Order not found"):
        super().__init__(message)


class OrderProductUnavailableError(Exception):
    def __init__(self, message: str = "Product is unavailable"):
        super().__init__(message)
