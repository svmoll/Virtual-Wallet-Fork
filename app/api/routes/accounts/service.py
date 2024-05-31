from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from ....core.models import Account
from decimal import Decimal


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
