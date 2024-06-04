from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from ...utils.responses import (
    AccountBlockedError,
    InsufficientFundsError,
    InvalidAmountError,
)
from ....core.models import Account, Withdrawal, Deposit
from decimal import Decimal
from datetime import datetime
import logging
import pytz

logger = logging.getLogger(__name__)


def withdraw_money_from_account(username: str, withdrawal_amount: Decimal, db: Session):
    try:
        account = get_account_by_username(username, db)

        if account.is_blocked:
            raise AccountBlockedError()

        if withdrawal_amount <= 0:
            raise InvalidAmountError()

        if account.balance < withdrawal_amount:
            raise InsufficientFundsError()

        withdrawal = Withdrawal(
            sender_account=username,
            amount=withdrawal_amount,
            transaction_date=datetime.now(pytz.utc),
        )
        db.add(withdrawal)

        account.balance -= withdrawal_amount

        db.commit()
        db.refresh(account)

        formatted_balance = f"{account.balance:.2f}"

        return formatted_balance

    except AccountBlockedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except InvalidAmountError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except InsufficientFundsError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


def add_money_to_account(username: str, deposit_amount: Decimal, db: Session):
    try:
        account = get_account_by_username(username, db)

        if account.is_blocked:
            raise AccountBlockedError()

        account.balance += deposit_amount

        deposit = Deposit(
            sender_account=username,
            amount=deposit_amount,
            transaction_date=datetime.now(pytz.utc),
        )
        db.add(deposit)

        db.commit()
        db.refresh(account)

        return account.balance

    except AccountBlockedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# Helper Functions
def get_account_by_username(username: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.username == username).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found!")

    return account
