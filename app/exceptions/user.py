class UserAlreadyExistsError(Exception):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message)

class UserNotFoundError(Exception):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)

class UnauthorizedUserError(Exception):
    def __init__(self, message: str = "Unauthorized user"):
        super().__init__(message)