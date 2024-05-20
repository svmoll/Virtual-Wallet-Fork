from sqlalchemy.orm import Session
from .schemas import UserDTO
from ...models.models import User
from ...utils.auth import hash_pass
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
            is_admin=user.is_admin,
            is_restricted=user.is_restricted
        )
        db.add(new_user)
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