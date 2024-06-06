from sqlalchemy.orm import Session
from app.core.db_dependency import get_db
from .schemas import UserDTO, UpdateUserDTO, UserShowDTO, UserFromSearchDTO, ContactDTO
from app.core.models import User, Account, Contact
from app.api.auth_service.auth import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends
from mailjet_rest import Client


def email_sender(user):
    api_key = 'cdcb4ffb9ac758e8750f5cf5bf07ac9f'
    api_secret = '8ec6183bbee615d0d62b2c72bee814c4'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "kis.team.telerik@gmail.com",
                    "Name": "MyPyWallet Admin"
                },
                "To": [
                    {
                        "Email": "kis.team.telerik@gmail.com",
                        "Name": "Kis"
                    }
                ],
                "Subject": f"New Registration UserID:{user.id}",
                "HTMLPart": f"<h3>New user {user.username} with id:{user.id} waits for confirmation</h3><br />May the delivery force be with you!",
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    mailjet.send.create(data=data)

def create(user: UserDTO, db: Session):
    try:
        hashed_password = hash_pass(user.password)

        new_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email,
            phone_number=user.phone_number,
            fullname=user.fullname
        )
        account = Account(username=user.username)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.add(account)
        db.commit()
        db.refresh(account)
        email_sender(new_user)
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

# Todo catch some other error exception
# Todo add messages to logger

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
        if update_info.fullname:
            user.fullname = update_info.fullname

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

    user = UserShowDTO(
        username=user.username,
        password="********",
        email=user.email,
        phone_number=user.phone_number,
        fullname=user.fullname
    )

    return user

def search_user(username: str = None, email: str = None, phone_number: str = None , db: Session = Depends(get_db)):

    if username:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User with that username was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif email:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User with that email was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)
    elif phone_number:
        user = db.query(User).filter_by(phone_number=phone_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="User with that phone number was not found")
        return UserFromSearchDTO(username=user.username, email=user.email)

def create_contact(contact_username: str, user_username: str, db: Session = Depends(get_db) ):
    user = db.query(User).filter_by(username=contact_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with that username was not found")

    existing_contact = db.query(Contact).filter(
        (Contact.user_username == user_username) & (Contact.contact_username == contact_username)
    ).first( )

    if existing_contact:
        raise HTTPException(status_code=404, detail="Contact already exists")

    new_contact = Contact(user_username=user_username, contact_username=contact_username)
    db.add(new_contact)

    try:
        db.commit( )
        return {"success": True}
    except IntegrityError:
        db.rollback( )
        raise HTTPException(status_code=400, detail="Unable to add contact")

def delete_contact(contact_username: str, user_username: str, db: Session = Depends(get_db) ):
    existing_contact = db.query(Contact).filter(
        (Contact.user_username == user_username) & (Contact.contact_username == contact_username)
    ).first()

    if existing_contact:
        db.delete(existing_contact)
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Contact does not exist")

def view(username: str, page: int | None = None, limit: int | None = None, db: Session = Depends(get_db)):
    if page is not None and limit is not None:
        offset = (page - 1) * limit
        contacts = db.query(Contact.contact_username).filter(Contact.user_username == username)

        # Apply pagination
        contacts = contacts.offset(offset).limit(limit)
        usernames = [ContactDTO.from_query_result(contact.contact_username) for contact in contacts]
        return usernames

    else:
        contacts = db.query(Contact.contact_username).filter(Contact.user_username == username)
        usernames = [ContactDTO.from_query_result(contact.contact_username) for contact in contacts]
        return usernames

