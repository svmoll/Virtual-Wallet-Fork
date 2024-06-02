from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from ...utils.responses import (
    AccountBlockedError,
    InsufficientFundsError,
    InvalidAmountError,
)
from ....core.models import Account
from decimal import Decimal
import logging

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

        account.balance -= withdrawal_amount

        db.commit()
        db.refresh(account)

        return account.balance

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


def add_money_to_account(username: str, deposit: Decimal, db: Session):
    try:
        account = get_account_by_username(username, db)

        if account.is_blocked:
            raise AccountBlockedError()

        account.balance += deposit

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
# find account by id(current_user) test
def get_account_by_id(current_user: UserViewDTO, db: Session):
    account = db.query(Account).filter_by(username=current_user.username).first()
    return account


def get_account_by_username(username: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(username == username).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found!")

    return account
