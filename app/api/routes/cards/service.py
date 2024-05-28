from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, Depends
from ....core.db_dependency import get_db
from ..users.schemas import UserDTO
from app.core.models import Card, User
from datetime import datetime, timedelta
import random
import string
from ...utils.responses import NotFound


def create_card_number():
    digits = string.digits 
    random_card_number = ''.join(random.choice(digits) for _ in range(16)) # random.randint(0,9)
    return random_card_number


def unique_card_number(db: Session):
    card_number = create_card_number()
    while db.query(Card).filter_by(card_number=card_number).first() is not None:
        card_number = create_card_number()
    return card_number


def create_expiration_date():
    return datetime.now() + timedelta(days=1826)


def create_cvv_number():
    digits = string.digits 
    random_cvv = ''.join(random.choice(digits) for _ in range(3))
    return random_cvv                                                   # hash the cvv. need to be stored somewhere to retrieve


def get_user_fullname(current_user, db: Session):
    user = db.query(User).filter_by(username=current_user.username).first()
    return user


def create(current_user: UserDTO, db: Session):
    expiration_date = create_expiration_date()
    card_number = unique_card_number(db)
    cvv_number = create_cvv_number()
    user = get_user_fullname(current_user, db)

    new_card = Card(
        account_id=current_user.id,
        card_number=card_number,
        expiration_date=expiration_date,
        card_holder=user.fullname,
        cvv=cvv_number,
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


def get_card_by_id(id:int, db: Session = Depends(get_db)) -> Card:
    card = db.query(Card).filter_by(id=id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found!")

    return card

def delete(id:int, db: Session):
    card_to_delete = get_card_by_id(id, db)

    db.delete(card_to_delete)
    db.commit()
    



