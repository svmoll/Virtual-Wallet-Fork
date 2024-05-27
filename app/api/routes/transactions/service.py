from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends
from app.core.models import Transaction
from app.core.db_dependency import get_db


def create_draft_transaction(
    sender_account: str, transaction: TransactionDTO, db: Session
):
    try:
        sender_account = sender_account

        transaction = Transaction(
            sender_account=sender_account,
            receiver_account=transaction.receiver_account,
            amount=transaction.amount,
            category_id=transaction.category_id,
            description=transaction.description,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except IntegrityError as e:
        db.rollback()
        if "receiver_account" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Receiver doesn't exist!"
            ) from e
        elif "category_id" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Category doesn't exist!"
            ) from e


def get_transaction_by_id(id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    return transaction


def update_draft_transaction(
    sender_account: str,
    transaction_id: int,
    updated_transaction: TransactionDTO,
    db: Session,
) -> Transaction:

    transaction_draft = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.sender_account == sender_account,
            Transaction.status == "draft",
        )
        .first()
    )

    if not transaction_draft:
        raise HTTPException(status_code=404, detail="Transaction draft not found!")

    try:
        transaction_draft.amount = updated_transaction.amount
        transaction_draft.receiver_account = updated_transaction.receiver_account
        transaction_draft.category_id = updated_transaction.category_id
        transaction_draft.description = updated_transaction.description

        db.commit()
        db.refresh(transaction_draft)

        return transaction_draft

    except IntegrityError as e:
        db.rollback()
        if "receiver_account" in str(e.orig):
            raise HTTPException(status_code=400, detail="Receiver doesn't exist!")
        elif "category_id" in str(e.orig):
            raise HTTPException(status_code=400, detail="Category doesn't exist!")
        else:
            raise HTTPException(status_code=400, detail="Database error occurred!")
