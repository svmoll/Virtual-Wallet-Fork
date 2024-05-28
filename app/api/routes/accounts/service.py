from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from app.api.routes.accounts.schemas import AccountViewDTO
from typing import Annotated
from ..users.schemas import UserDTO
from ...auth_service import auth

def withdrawal_request(
    withdrawal_amount: float,
    account: AccountViewDTO,
    db: Session = Depends(get_db)
    ):
    if account.is_blocked:
        raise HTTPException(status_code=400, detail=f"Account is not allowed to withdraw. Contact Customer Support.")
    elif withdrawal_amount < 0:
        raise HTTPException(status_code=400, detail=f"You are requesting to withdraw a negative amount.")
    elif withdrawal_amount > account.balance:
        raise HTTPException(status_code=400, detail=f"Insufficient amount to withdraw {withdrawal_amount} leva")
    
    account.balance -= withdrawal_amount

    db.commit()
    db.refresh(account.balance)
