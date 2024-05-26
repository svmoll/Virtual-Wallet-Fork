from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.db_dependency import get_db
from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from .service import create_draft_transaction as cdt
from ..users.schemas import UserDTO, UserViewDTO
from ...auth_service import auth


transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.post("/draft")
def create_draft_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction: TransactionDTO,
    db: Session = Depends(get_db),
):

    created_draft_transaction = cdt(current_user.username, transaction, db)

    return f"You are about to send {created_draft_transaction.amount} to {created_draft_transaction.receiver_account}"
