class ReviewNotFoundError(Exception):
    def __init__(self, message: str = "Review not found"):
        super().__init__(message)


class ReviewAlreadyExistsError(Exception):
    def __init__(
        self,
        message: str = "User already has a review for this product",
    ):
        super().__init__(message)


class ReviewPermissionDeniedError(Exception):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)