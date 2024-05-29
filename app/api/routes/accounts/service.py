from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.db_dependency import get_db
from app.api.routes.accounts.schemas import AccountViewDTO
from ..users.schemas import UserDTO
from ....core.models import Account


#find account by id(current_user) test
def get_account_by_id(current_user: UserDTO, db: Session):
    account = db.query(Account).filter_by(username=current_user.username).first()
    return account
    

def withdrawal_request(
    withdrawal_amount: float,
    current_user: UserDTO,
    db: Session = Depends(get_db)
    ):
    
    account = get_account_by_id(current_user, db)

    if account.is_blocked:
        raise HTTPException(status_code=400, detail=f"Account is blocked. Contact Customer Support.")
    elif withdrawal_amount < 0:
        raise HTTPException(status_code=400, detail=f"You are requesting to withdraw a negative amount.")
    elif withdrawal_amount > account.balance:
        raise HTTPException(status_code=400, detail=f"Insufficient amount to withdraw {withdrawal_amount} leva")
    
    account.balance -= withdrawal_amount

    db.commit()
    db.refresh(account.balance)
