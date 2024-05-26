from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from core.models import Transaction


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
