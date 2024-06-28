from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Request, Query
from fastapi.responses import JSONResponse, Response
from app.core.db_dependency import get_db
from .schemas import TransactionDTO, RecurringTransactionDTO
from sqlalchemy.orm import Session

from .service import (
    create_draft_transaction,
    update_draft_transaction,
    confirm_draft_transaction,
    delete_draft,
    accept_incoming_transaction,
    decline_incoming_transaction,
    create_recurring_transaction,
    cancelling_recurring_transaction,
    view_recurring_transactions,
    view_transactions,
)

# from . import service
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


@transaction_router.post("/{transaction_id}/accept")
def accept_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction_id: int,
    db: Session = Depends(get_db),
):
    new_balance = accept_incoming_transaction(current_user.username, transaction_id, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Your balance is {new_balance}."},
    )


@transaction_router.post("/{transaction_id}/decline")
def decline_transaction(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    transaction_id: int,
    db: Session = Depends(get_db),
):
    decline_incoming_transaction(current_user.username, transaction_id, db)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@transaction_router.post("/recurring_transactions/")
async def make_recurring_transaction(
    request: Request,
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    recurring_transaction: RecurringTransactionDTO,
    db: Session = Depends(get_db),
):
    scheduler = request.app.state.scheduler

    return create_recurring_transaction(
        current_user.username, recurring_transaction, db, scheduler
    )


@transaction_router.get("/recurring_transactions/")
def display_recurring_transactions(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):
    transactions = view_recurring_transactions(current_user.username, db)

    if len(transactions) < 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "There are no recurring transactions at this moment."},
        )
    return transactions


@transaction_router.delete("/recurring_transactions/")
async def cancel_recurring_transaction(
    request: Request,
    recurring_transaction_id: int,
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):
    scheduler = request.app.state.scheduler

    cancelling_recurring_transaction(
        recurring_transaction_id, current_user.username, db, scheduler
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@transaction_router.get("/")
def view_transaction_history(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    receiver: Optional[str] = Query(None, description="Username of receiver"),
    period: Optional[str] = Query(None, description="Username of sender"),
    direction: Optional[str] = Query(
        None, description="Direction (Only accepts 'incoming' or 'outgoing')"
    ),
    sort: Optional[str] = Query(None, description="Sort order"),
    page: Optional[int] = Query(None, description="Page Number"),
    limit: Optional[int] = Query(None, description="Limit on page"),
    db: Session = Depends(get_db),
):

    transactions = view_transactions(
        current_user.username, receiver, period, direction, sort, limit, page, db
    )

    if not transactions:
        return JSONResponse(
            status_code=404, content={"message": "Transactions not found"}
        )

    return transactions
