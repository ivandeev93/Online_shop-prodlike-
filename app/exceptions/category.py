class CategoryNotFoundError(Exception):
    def __init__(self, message: str = "Category not found"):
        super().__init__(message)


class CategoryAlreadyExistsError(Exception):
    def __init__(self, message: str = "Category already exists"):
        super().__init__(message)