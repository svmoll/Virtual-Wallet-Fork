from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.routes.users.schemas import UserFromSearchDTO
from app.core.db_dependency import get_db
from app.core.models import User

def check_is_admin(id: int, db: Session = Depends(get_db)) -> bool:
    user = db.query(User).filter(User.id == id).first()
    if user.is_admin:
        return True
    else:
        return False
def search_user(username: str = None, email: str = None, phone_number: str = None, page:int | None = None, limit:int | None = None, db: Session = Depends(get_db)):
    if username:
        user = db.query(User).filter_by(username=username).first( )
        if not user:
            raise HTTPException(status_code=404, detail="User with that username was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif email:
        user = db.query(User).filter_by(email=email).first( )
        if not user:
            raise HTTPException(status_code=404, detail="User with that email was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif phone_number:
        user = db.query(User).filter_by(phone_number=phone_number).first( )
        if not user:
            raise HTTPException(status_code=404, detail="User with that phone number was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)
    else:
        query = db.query(User)
        if page is not None and limit is not None:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
        users = query.all( )
        return (UserFromSearchDTO(username=user.username, email=user.email) for user in users)


def status(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with that username was not found")

    if user.is_blocked == 0:
        user.is_blocked = 1
        db.commit()
        db.refresh(user)
        return f"{user.username} is blocked"
    else:
        user.is_blocked = 0
        db.commit()
        db.refresh(user)
        return f"{user.username} is unblocked"