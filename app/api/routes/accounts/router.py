from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from app.api.routes.accounts.service import (
    withdraw_money_from_account,
    add_money_to_account,
)
from typing import Annotated
from ..users.schemas import UserViewDTO
from ...auth_service import auth
from decimal import Decimal


account_router = APIRouter(prefix="/accounts", tags=["Accounts"])


@account_router.post("/withdrawal")
def withdraw_money(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    withdrawal_amount: Decimal = Body(),
    db: Session = Depends(get_db),
):
    updated_balance = withdraw_money_from_account(
        current_user.username, withdrawal_amount, db
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Your current balance is {updated_balance}"},
    )


@account_router.post("/deposit")
def deposit_money(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    deposit_amount: Decimal = Body(),
    db: Session = Depends(get_db),
):

    updated_balance = add_money_to_account(current_user.username, deposit_amount, db)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Your current balance is {updated_balance}"},
    )
