class CartItemNotFoundError(Exception):
    def __init__(self, message: str = "Cart item not found"):
        super().__init__(message)


class InsufficientStockError(Exception):
    def __init__(self, message: str = "Insufficient product stock"):
        super().__init__(message)
