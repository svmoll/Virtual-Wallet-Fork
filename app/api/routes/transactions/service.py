from datetime import datetime
import pytz
from decimal import Decimal
from mailjet_rest import Client
from .schemas import TransactionDTO
from ...utils.responses import DatabaseError, InsufficientFundsError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, Depends
from app.core.models import Account, Transaction, User
from ..accounts.service import get_account_by_username
from app.core.db_dependency import get_db


def decline_email_sender(user, transaction):
    api_key = 'cdcb4ffb9ac758e8750f5cf5bf07ac9f'
    api_secret = '8ec6183bbee615d0d62b2c72bee814c4'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "kis.team.telerik@gmail.com",
                    "Name": "MyPyWallet Admin"
                },
                "To": [
                    {
                        "Email": f"{user.email}",
                        "Name": f"{user.fullname}"
                    }
                ],
                "Subject": f"Declined Transaction",
                "HTMLPart": f"<h3>Your transaction with ID:{transaction.id} was declined by the receiver</h3>",
                "CustomID": f"UserID: {user.id}"
            }
        ]
    }
    mailjet.send.create(data=data)

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
        else:
            raise HTTPException(status_code=400, detail="Database error occurred!")


def update_draft_transaction(
    sender_account: str,
    transaction_id: int,
    updated_transaction: TransactionDTO,
    db: Session,
) -> Transaction:

    transaction_draft = get_draft_transaction_by_id(transaction_id, sender_account, db)

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


def confirm_draft_transaction(sender_account: str, transaction_id: int, db: Session):

    try:
        transaction_draft = get_draft_transaction_by_id(
            transaction_id, sender_account, db
        )
        account = get_account_by_username(sender_account, db)

        if account.balance < transaction_draft.amount:
            raise InsufficientFundsError()

        transaction_draft.status = "pending"
        account.balance -= transaction_draft.amount

        db.commit()
        db.refresh(transaction_draft)

        return transaction_draft

    except InsufficientFundsError:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error occurred!")

    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def delete_draft(sender_account: str, transaction_id: int, db: Session):
    transaction_draft = get_draft_transaction_by_id(transaction_id, sender_account, db)

    db.delete(transaction_draft)
    db.commit()


def accept_incoming_transaction(
    receiver_account: str, transaction_id: int, db: Session
):
    incoming_transaction = get_incoming_transaction_by_id(
        receiver_account, transaction_id, db
    )
    account = get_account_by_username(receiver_account, db)

    account.balance = account.balance + incoming_transaction.amount

    incoming_transaction.status = "completed"
    incoming_transaction.transaction_date = datetime.now(pytz.utc)

    try:
        db.commit()
        db.refresh(account)
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Database operation failed") from e

    return account.balance


def decline_incoming_transaction(
    receiver_account: str, transaction_id: int, db: Session
):
    incoming_transaction = get_incoming_transaction_by_id(
        receiver_account, transaction_id, db
    )
    sender_account = get_account_by_username(incoming_transaction.sender_account, db)

    sender_account.balance += incoming_transaction.amount
    incoming_transaction.status = "declined"
    incoming_transaction.transaction_date = datetime.now(pytz.utc)
    sender = db.query(User).filter(User.username==incoming_transaction.sender_account).first()
    decline_email_sender(sender, incoming_transaction)
    db.commit()



# Helper Functions
def get_draft_transaction_by_id(
    transaction_id: int, sender_account: str, db: Session = Depends(get_db)
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

    return transaction_draft


def get_incoming_transaction_by_id(
    receiver_account: str, transaction_id: int, db: Session = Depends(get_db)
) -> Transaction:
    incoming_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.receiver_account == receiver_account,
            Transaction.status == "pending",
        )
        .first()
    )

    if not incoming_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found!")

    return incoming_transaction
