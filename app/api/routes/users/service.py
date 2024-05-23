from sqlalchemy.orm import Session
from .schemas import UserDTO
from app.core.models import User , Account
from app.api.auth_service.auth import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def create(user: UserDTO, db: Session):
    try:
        hashed_password = hash_pass(user.password)

        new_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email,
            phone_number=user.phone_number,
        )
        account = Account(username=user.username)
        db.add_all([new_user, account])
        # db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()
        if "phone_number" in str(e.orig):
            raise HTTPException(status_code=400, detail="Phone number already exists") from e
        elif "username" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already exists") from e
        elif "email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists") from e
        else:
            raise HTTPException(status_code=400, detail="Could not complete registration") from e