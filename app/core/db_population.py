from sqlalchemy.orm import Session
from .models import Account, User, Category
from ..api.auth_service.auth import hash_pass


def initialize_special_accounts(db: Session):
    # Check if the cash_withdrawal account exists
    cash_account = db.query(Account).filter_by(username="cash_withdrawal").first()
    if not cash_account:
        # Create the cash_withdrawal account if it doesn't exist
        cash_user = User(
            username="cash_withdrawal",
            password="testPassword",
            email="some.email@gmail.com",
            phone_number="000",
            fullname="Cash Withdrawal",
            is_admin=False,
            is_restricted=False,
        )
        db.add(cash_user)
        db.commit()

        cash_account = Account(username="cash_withdrawal", balance=0, is_blocked=False)
        db.add(cash_account)
        db.commit()
