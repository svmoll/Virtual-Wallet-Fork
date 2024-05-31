from fastapi import Response


class Forbidden(Response):
    def __init__(self, content=""):
        super().__init__(status_code=403, content=content)


class BadRequest(Response):
    def __init__(self, content=""):
        super().__init__(status_code=400, content=content)


class NotFound(Response):
    def __init__(self, content=""):
        super().__init__(status_code=404, content=content)


class Unauthorized(Response):
    def __init__(self, content=""):
        super().__init__(status_code=401, content=content)


class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204)


class InternalServerError(Response):
    def __init__(self):
        super().__init__(status_code=500)


class DatabaseError(Exception):
    """Exception raised for database-related errors."""

    def __init__(self, message="Database operation failed", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InsufficientFundsError(Exception):
    def __init__(self, message="Insufficient funds", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
