from datetime import datetime, date, time
import pytz
from enum import Enum
from decimal import Decimal
from mailjet_rest import Client
import logging
from app.core.database import SessionLocal
from decimal import Decimal
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import desc, select, Table
from .schemas import (
    TransactionDTO,
    RecurringTransactionDTO,
    RecurringTransactionView,
    TransactionView,
)
from ...utils.responses import DatabaseError, InsufficientFundsError
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, Depends
from app.core.models import (
    Transaction,
    User,
    RecurringTransaction,
    Account,
    BaseTransaction,
)
from ..accounts.service import get_account_by_username
from app.core.db_dependency import get_db
from app.core.database import engine, metadata


class Direction(str, Enum):
    outgoing = "outgoing"
    incoming = "incoming"


# TimeZone Settings
utc_time = datetime.now(pytz.utc)
desired_timezone = pytz.timezone("Europe/Sofia")


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
    incoming_transaction.transaction_date = datetime.now(pytz.utc).astimezone(
        desired_timezone
    )

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
    incoming_transaction.transaction_date = datetime.now(pytz.utc).astimezone(
        desired_timezone
    )
    sender = (
        db.query(User)
        .filter(User.username == incoming_transaction.sender_account)
        .first()
    )
    decline_email_sender(sender, incoming_transaction)
    db.commit()


def create_recurring_transaction(
    sender_account: str,
    recurring_transaction: RecurringTransactionDTO,
    db: Session,
    scheduler: AsyncIOScheduler,
):
    try:
        custom_days = recurring_transaction.custom_days
        start_date = recurring_transaction.start_date
        start_datetime = datetime.combine(start_date, time.min)
        recurring_interval = recurring_transaction.recurring_interval

        if custom_days is not None:
            str_recurring_interval = f"{custom_days} days"
        else:
            str_recurring_interval = recurring_interval

        recurring_transaction = RecurringTransaction(
            sender_account=sender_account,
            receiver_account=recurring_transaction.receiver_account,
            amount=recurring_transaction.amount,
            category_id=recurring_transaction.category_id,
            description=recurring_transaction.description,
            recurring_interval=str_recurring_interval,
            status="ongoing",
        )

        db.add(recurring_transaction)
        db.commit()
        db.refresh(recurring_transaction)

        job_id = f"recurring_transaction_{recurring_transaction.id}"
        trigger = get_trigger(recurring_interval, custom_days)
        scheduler.add_job(
            process_recurring_transaction,
            trigger,
            args=[
                sender_account,
                recurring_transaction.receiver_account,
                recurring_transaction.amount,
                recurring_transaction.category_id,
                recurring_transaction.description,
            ],
            id=job_id,
            start_date=start_datetime,
        )

        recurring_transaction.job_id = job_id
        db.commit()

        return recurring_transaction

    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database error occurred: {e}")
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"An unexpected error occurred: {e}")
        raise


async def process_recurring_transaction(
    sender_account: str,
    receiver_account: str,
    amount: Decimal,
    category_id: int,
    description: str,
    db: Session = SessionLocal(),
):
    try:
        sender = db.query(Account).filter(Account.username == sender_account).first()

        receiver = (
            db.query(Account).filter(Account.username == receiver_account).first()
        )

        if sender.balance >= amount:
            sender.balance -= amount
            receiver.balance += amount
            transaction = Transaction(
                sender_account=sender_account,
                receiver_account=receiver_account,
                amount=amount,
                category_id=category_id,
                description=description,
                status="completed",
                transaction_date=datetime.now(pytz.utc).astimezone(desired_timezone),
            )
            db.add(transaction)
            db.commit()
        else:
            logging.info(
                f"The account of {sender_account} does not have sufficient funds."
            )
            sender = db.query(User).filter(User.username == sender_account).first()
            notify_failed_recurring_transaction(sender, amount, receiver_account)
            raise InsufficientFundsError()

    except (ValueError, InsufficientFundsError) as e:
        logging.error(f"Transaction failed: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
        db.rollback()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        db.rollback()


def cancelling_recurring_transaction(
    recurring_transaction_id: int,
    sender_account: str,
    db: Session,
    scheduler: AsyncIOScheduler,
):
    recurring_transaction = get_recurring_transaction_by_id(
        recurring_transaction_id, sender_account, db
    )

    scheduler.remove_job(recurring_transaction.job_id)

    recurring_transaction.status = "cancelled"
    recurring_transaction.is_active = False
    db.commit()
    db.refresh(recurring_transaction)


def view_recurring_transactions(username: str, db: Session):
    jobs_table = Table("apscheduler_jobs", metadata, autoload_with=engine)

    result = (
        db.query(RecurringTransaction, jobs_table.c.next_run_time)
        .filter_by(sender_account=username, status="ongoing")
        .join(jobs_table, RecurringTransaction.job_id == jobs_table.c.id)
        .all()
    )

    formatted_result = []
    for rt, next_run_time in result:
        formatted_result.append(
            RecurringTransactionView(
                id=rt.id,
                receiver=rt.receiver_account,
                amount=rt.amount,
                category_id=rt.category_id,
                description=rt.description,
                recurring_interval=rt.recurring_interval,
                next_run_time=datetime.fromtimestamp(float(next_run_time)).date(),
            )
        )

    return formatted_result


def view_transactions(
    username,
    receiver,
    period,
    direction,
    sort,
    page,
    limit,
    db: Session = Depends(get_db),
):
    query = db.query(BaseTransaction).filter(
        BaseTransaction.type.in_(["transaction", "withdrawal", "deposit"])
    )

    if receiver:
        user = db.query(User).filter_by(username=receiver).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that username was not found"
            )

    # Filtering based on query parameters
    if receiver:
        query = query.filter(Transaction.receiver_account == receiver)
    # if period:
    #     to be implemented in the future
    if direction == Direction.incoming:
        query = query.filter(Transaction.receiver_account == username)
    if direction == Direction.outgoing:
        query = query.filter(Transaction.sender_account == username)

    # Sorting
    if sort:
        if sort == "date_asc":
            query = query.order_by(Transaction.transaction_date.asc())
        elif sort == "date_desc":
            query = query.order_by(Transaction.transaction_date.desc())
        elif sort == "amount_asc":
            query = query.order_by(Transaction.amount.asc())
        elif sort == "amount_desc":
            query = query.order_by(Transaction.amount.desc())

    if page is not None and limit is not None:
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

    transactions = query.all()

    transactions_views = [
        TransactionView(
            id=transaction.id,
            sender=transaction.sender_account,
            receiver=transaction.receiver_account,
            amount=transaction.amount,
            transaction_date=transaction.transaction_date,
            type=transaction.type,
            status=transaction.status,
        )
        for transaction in transactions
    ]

    return transactions_views


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


def get_recurring_transaction_by_id(
    recurring_transaction_id: int, sender_account: str, db: Session = Depends(get_db)
) -> RecurringTransaction:
    recurring_transaction = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.id == recurring_transaction_id,
            RecurringTransaction.sender_account == sender_account,
            RecurringTransaction.status == "ongoing",
        )
        .first()
    )

    if not recurring_transaction:
        raise HTTPException(status_code=404, detail="Recurring transaction not found!")

    return recurring_transaction


def get_trigger(recurring_interval: str, custom_days: int = None):
    interval_mapping = {
        "daily": IntervalTrigger(days=1),
        "weekly": IntervalTrigger(weeks=1),
        "monthly": CronTrigger(day=1),
        "yearly": CronTrigger(year="*"),
        "custom": IntervalTrigger(days=custom_days) if custom_days else None,
        "minute": IntervalTrigger(seconds=60),
    }
    return interval_mapping.get(recurring_interval)


def decline_email_sender(user, transaction):
    api_key = "cdcb4ffb9ac758e8750f5cf5bf07ac9f"
    api_secret = "8ec6183bbee615d0d62b2c72bee814c4"
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {
                    "Email": "kis.team.telerik@gmail.com",
                    "Name": "MyPyWallet Admin",
                },
                "To": [{"Email": f"{user.email}", "Name": f"{user.fullname}"}],
                "Subject": f"Declined Transaction",
                "HTMLPart": f"<h3>Your transaction with ID:{transaction.id} was declined by the receiver</h3>",
                "CustomID": f"UserID: {user.id}",
            }
        ]
    }
    mailjet.send.create(data=data)


def notify_failed_recurring_transaction(user: User, amount: Decimal, receiver: str):
    api_key = "cdcb4ffb9ac758e8750f5cf5bf07ac9f"
    api_secret = "8ec6183bbee615d0d62b2c72bee814c4"
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {
                    "Email": "kis.team.telerik@gmail.com",
                    "Name": "MyPyWallet Admin",
                },
                "To": [{"Email": f"{user.email}", "Name": f"{user.fullname}"}],
                "Subject": f"Failed Transaction",
                "HTMLPart": f"<h3>Your recurring transaction of {amount} to {receiver} was interrupted due to insufficient funds!</h3>",
                "CustomID": f"UserID: {user.id}",
            }
        ]
    }
    mailjet.send.create(data=data)
