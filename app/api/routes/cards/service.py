from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, Depends
from core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from .schemas import CardDTO
from app.core.models import Card, User
from datetime import datetime, timedelta
import random
import string

def generate_card_number():
    digits = string.digits 
    random_card_number = ''.join(random.choice(digits) for _ in range(16)) # random.randint(0,9)
    return random_card_number


def unique_card_number(db: Session = Depends(get_db)):
    card_number = generate_card_number()
    # existing_cards = select(Card) # complete this
    # while card_number in existing_cards:
    #     unique_card_number = generate_card_number()
    while db.query(Card).filter_by(card_number=card_number).first() is not None:
        card_number = generate_card_number()
    return unique_card_number


def generate_cvv_number():
    digits = string.digits 
    random_cvv = ''.join(random.choice(digits) for _ in range(3))
    return random_cvv                                                   # hash the cvv. need to be stored somewhere to retrieve


def user_fullname(current_user, db: Session):
    user = db.query(User).filter_by(id=current_user.id).first()
    return user


def create(current_user: UserViewDTO, db: Session):
    generated_expiration_date = datetime.now() + timedelta(days=1826)
    generated_unique_card_number = generate_card_number()
    generated_cvv_number = generate_cvv_number()
    user = user_fullname(current_user, db)

    new_card = Card(
        account_id=current_user.id,
        card_number=generated_unique_card_number,
        expiration_date=generated_expiration_date,
        card_holder=user.fullname,
        cvv= generated_cvv_number,
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

