from sqlalchemy.orm import Session
from app.core.db_dependency import get_db
from .schemas import UserDTO, UpdateUserDTO
from app.core.models import User, Account
from app.api.auth_service.auth import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends


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
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()
        if "phone_number" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Phone number already exists"
            ) from e
        elif "username" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Username already exists"
            ) from e
        elif "email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists") from e
        else:
            raise HTTPException(
                status_code=400, detail="Could not complete registration"
            ) from e

            raise HTTPException(
                status_code=400, detail="Could not complete registration"
            ) from e


def update_user(id, update_info: UpdateUserDTO, db: Session = Depends(get_db)):
    try:
        # Retrieve the existing user
        user = db.query(User).filter_by(id=id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user's attributes
        if update_info.password:
            user.password = hash_pass(update_info.password)
        if update_info.email:
            user.email = update_info.email
        if update_info.phone_number:
            user.phone_number = update_info.phone_number

        # Commit the changes to the database
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError as e:
        db.rollback()
        if "phone_number" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Phone number already exists"
            ) from e
        elif "username" in str(e.orig):
            raise HTTPException(
                status_code=400, detail="Username already exists"
            ) from e
        elif "email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists") from e
        else:
            raise HTTPException(
                status_code=400, detail="Could not complete update"
            ) from e


def get_user(id, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
