from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid authentication credentials",
        headers: dict = None,
    ):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class ForbiddenException(HTTPException):
    def __init__(
        self,
        detail: str = "You don't have permission to access this resource",
        headers: dict = None,
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class NotFoundException(HTTPException):
    def __init__(
        self,
        detail: str = "Resource not found",
        headers: dict = None,
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class BadRedquestException(HTTPException):
    def __init__(
        self,
        detail: str = "Bad request",
        headers: dict = None,
    ):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)
