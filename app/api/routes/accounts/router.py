from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from app.api.routes.accounts.schemas import AccountViewDTO
from app.api.routes.accounts.service import withdrawal_request
from typing import Annotated
from ..users.schemas import UserDTO
from ...auth_service import auth



account_router = APIRouter(prefix="/accounts", tags=["Accounts"])

@account_router.put("/withdrawal")
def create_withdrawal(
    current_user: Annotated[UserDTO, Depends(auth.get_user_or_raise_401)], 
    db: Session = Depends(get_db),
    withdrawal_amount: float = Body()
    ):
    withdrawal_request(withdrawal_amount,current_user,db)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"The withdrawal of {withdrawal_amount} leva is received and being processed."
        },
    )

