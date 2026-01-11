from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, user_id: int = None, username: str = None):
        identifier = f"id={user_id}" if user_id else f"username={username}"
        detail = f"User with {identifier} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UserAlreadyExistsException(HTTPException):
    def __init__(self, field: str, value: str):
        detail = f"User with {field}='{value}' already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

