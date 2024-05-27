from fastapi import HTTPException, FastAPI
from starlette.responses import JSONResponse

app = FastAPI()


class CustomValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=422, detail= message)

class UsernameValidationError(CustomValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)

class EmailValidationError(CustomValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)

class PasswordValidationError(CustomValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)

class PhoneNumberValidationError(CustomValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)

class FullNameValidationError(CustomValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)

@app.exception_handler(CustomValidationError)
async def custom_validation_exception_handler(exc: CustomValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )