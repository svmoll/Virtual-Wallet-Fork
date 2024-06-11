from enum import Enum
from fastapi import HTTPException, Depends
from mailjet_rest import Client
from sqlalchemy.orm import Session
from app.api.routes.admin.schemas import TransactionViewDTO
from app.api.routes.users.schemas import UserFromSearchDTO
from app.core.db_dependency import get_db
from app.core.models import User, Account, Transaction


def deny_email_sender(user, transaction):
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
                "Subject": f"Denied Transaction",
                "HTMLPart": f"<h3>Your transaction with ID:{transaction.id} was denied</h3>",
                "CustomID": f"UserID: {user.id}",
            }
        ]
    }
    mailjet.send.create(data=data)


def confirmed_email_sender(user):
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
                "Subject": f"Confirmed Registration",
                "HTMLPart": f"<h3>Your Registration is complete, now you can freely use the app</h3><br />May the delivery force be with you!",
                "CustomID": f"UserID: {user.id}",
            }
        ]
    }
    mailjet.send.create(data=data)


class FlaggedOption(str, Enum):
    yes = "yes"
    no = "no"


def check_is_admin(id: int, db: Session = Depends(get_db)) -> bool:
    user = db.query(User).filter(User.id == id).first()
    if user.is_admin:
        return True
    else:
        return False


def search_user(
    username: str = None,
    email: str = None,
    phone_number: str = None,
    page: int | None = None,
    limit: int | None = None,
    db: Session = Depends(get_db),
):
    if username:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that username was not found"
            )
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif email:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that email was not found"
            )
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif phone_number:
        user = db.query(User).filter_by(phone_number=phone_number).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that phone number was not found"
            )
        return UserFromSearchDTO(username=user.username, email=user.email)
    else:
        query = db.query(User)
        if page is not None and limit is not None:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
        users = query.all()
        return (
            UserFromSearchDTO(username=user.username, email=user.email)
            for user in users
        )


def status(username: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter_by(username=username).first()
    if not account:
        raise HTTPException(
            status_code=404, detail="Account with that username was not found"
        )

    if account.is_blocked == 0:
        account.is_blocked = 1
        db.commit()
        db.refresh(account)
        return f"{account.username} is blocked"
    else:
        account.is_blocked = 0
        db.commit()
        db.refresh(account)
        return f"{account.username} is unblocked"


def view_transactions(
    sender, receiver, status, flagged, sort, page, limit, db: Session = Depends(get_db)
):
    query = db.query(Transaction)

    if sender:
        user = db.query(User).filter_by(username=sender).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that username was not found"
            )
    if receiver:
        user = db.query(User).filter_by(username=receiver).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User with that username was not found"
            )

    # Filtering based on query parameters
    if sender:
        query = query.filter(Transaction.sender_account == sender)
    if receiver:
        query = query.filter(Transaction.receiver_account == receiver)
    if status:
        query = query.filter(Transaction.status == status)
    if flagged == FlaggedOption.yes:
        query = query.filter(Transaction.is_flagged == 1)
    if flagged == FlaggedOption.no:
        query = query.filter(Transaction.is_flagged == 0)

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

    # Pagination
    if page is not None and limit is not None:
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

    transactions = query.all()

    # TransactionDTO schema to structure the response
    transactions_dto = [
        TransactionViewDTO(
            id=transaction.id,
            sender=transaction.sender_account,
            receiver=transaction.receiver_account,
            amount=transaction.amount,
            status=transaction.status,
            is_flagged=transaction.is_flagged,
            type=transaction.type,
            transaction_date=transaction.transaction_date,
        )
        for transaction in transactions
    ]

    return transactions_dto


def deny_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter_by(id=transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=404, detail="Transaction with that id was not found"
        )
    if transaction.status != "pending":
        raise HTTPException(
            status_code=400, detail="Cannot denied non pending transactions"
        )

    transaction.status = "denied"
    db.commit()
    user = db.query(User).filter_by(username=transaction.sender_account).first()
    deny_email_sender(user, transaction)


def confirm_user(id, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with that id was not found")
    user.is_restricted = 0
    account = db.query(Account).filter_by(username=user.username).first()
    account.is_blocked = 0
    db.commit()
    confirmed_email_sender(user)
