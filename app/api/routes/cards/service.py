from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from ....core.db_dependency import get_db
from ..users.schemas import UserViewDTO
from app.core.models import Card, User
from jose import jwt
from datetime import timedelta, date
import random
import string



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7"
ALGORITHM = "HS256"

def create_card_number():
    digits = string.digits 
    random_card_number = ''.join(random.choice(digits) for _ in range(16)) # random.randint(0,9)
    formatted_card_number = '-'.join(random_card_number[i:i+4] for i in range(0, 16, 4))
    return formatted_card_number


def unique_card_number(db: Session):
    card_number = create_card_number()
    while db.query(Card).filter_by(card_number=card_number).first() is not None:
        card_number = create_card_number()
    return card_number


def create_expiration_date():
    return date.today() + timedelta(days=1826)


def create_cvv_number():
    digits = string.digits 
    random_cvv = ''.join(random.choice(digits) for _ in range(3))
    formatted_cvv = encrypt_cvv(random_cvv)
    return formatted_cvv

def encrypt_cvv(random_cvv):
    to_encode = {"cvv": random_cvv}
    # resulting_cvv = sha1(random_cvv.encode("utf-8")).hexdigest()
    encoded_cvv = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_cvv


def decrypt_cvv(cvv):
    decoded_cvv = jwt.decode(cvv, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_cvv


def get_user_fullname(current_user, db: Session):
    user = db.query(User).filter_by(username=current_user.username).first()
    return user


def create(current_user: UserViewDTO, db: Session):
    expiration_date = create_expiration_date()
    card_number = unique_card_number(db)
    cvv_number = create_cvv_number(card_number, expiration_date)
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


def get_card_by_id(id:int, db: Session) -> Card:
    card = db.query(Card).filter_by(id=id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found!")

    return card

def delete(id:int, db: Session):
    card_to_delete = get_card_by_id(id, db)

    db.delete(card_to_delete)
    db.commit()


def get_view(current_user: UserViewDTO, db: Session):
    cards_list = db.query(Card).filter(Card.account_id==current_user.id).all()
    for i in cards_list:
        print(i)

    cards_list = [{
            "card_number": card.card_number,
            "expiration_date": card.expiration_date.isoformat(),
            "cvv": decrypt_cvv(card.cvv)["cvv"]
            } for card in cards_list]

    return cards_list

