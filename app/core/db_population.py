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

    admin = db.query(User).filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            password=hash_pass("Admin1!!"),
            email="kis.team.telerik@gmail.com",
            phone_number="00000000000",
            fullname="Admin",
            is_admin=True,
            is_restricted=False,
        )
        db.add(admin)
        db.commit()


def initialize_other_category(db: Session):
    # Check if the 'Other' category exists
    other_category = db.query(Category).filter_by(name="Other").first()
    if not other_category:
        # Create the 'Other' category if it doesn't exist
        other = Category(
            id=1,
            name="Other",
            color_hex=None,
        )
        db.add(other)
        db.commit()
