from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from ...utils.responses import AccountBlockedError
from ....core.models import Account
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def withdrawal_request(
    withdrawal_amount: Decimal, current_user: UserViewDTO, db: Session = Depends(get_db)
):

    account = get_account_by_id(current_user, db)

    if account.is_blocked == True:
        raise HTTPException(
            status_code=400, detail=f"Account is blocked. Contact Customer Support."
        )
    if withdrawal_amount <= 0:
        raise HTTPException(
            status_code=400, detail=f"Withdrawals should be a positive number."
        )
    if withdrawal_amount > account.balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient amount to withdraw {withdrawal_amount} leva.",
        )

    account.balance -= withdrawal_amount

    db.commit()

    return account


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
