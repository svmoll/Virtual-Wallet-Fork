from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from app.core.db_dependency import get_db
from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from .service import (
    create_draft_transaction,
    update_draft_transaction,
    confirm_draft_transaction,
    delete_draft,
)
from ..users.schemas import UserViewDTO
from ...auth_service import auth

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.post("/draft", status_code=status.HTTP_201_CREATED)
def make_draft_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction: TransactionDTO,
    db: Session = Depends(get_db),
):

    created_draft_transaction = create_draft_transaction(
        current_user.username, transaction, db
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"You are about to send {created_draft_transaction.amount} to {created_draft_transaction.receiver_account} [Draft ID: {created_draft_transaction.id}]"
        },
    )


@transaction_router.put("/{transaction_id}", status_code=status.HTTP_200_OK)
def edit_draft_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction_id: int,
    updated_transaction: TransactionDTO,
    db: Session = Depends(get_db),
):
    updated_draft = update_draft_transaction(
        current_user.username, transaction_id, updated_transaction, db
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"You've successfully edited Draft ID: {updated_draft.id}! You are about to send {updated_draft.receiver_account} {updated_draft.amount}$"
        },
    )


@transaction_router.post("/{transaction_id}/confirm", status_code=status.HTTP_200_OK)
def confirm_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction_id: int,
    db: Session = Depends(get_db),
):

    confirmed_transaction = confirm_draft_transaction(
        current_user.username, transaction_id, db
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Your transfer to {confirmed_transaction.receiver_account} is pending!"
        },
    )


@transaction_router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction_id: int,
    db: Session = Depends(get_db),
):

    delete_draft(current_user.username, transaction_id, db)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
