# Database models
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from core.config import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(length=25), unique=True, index=True, nullable=False)
    password = Column(String(length=200), nullable=False,nullable=False)
    email = Column(String(length=50), unique=True, index=True, nullable=False)
    phone_number = Column(String(length=100), unique=True, nullable=False)
    photo_path = Column(String(length=300))
    is_admin = Column(Boolean, default=False, nullable=False)
    is_restricted = Column(Boolean, default=False, nullable=False)

    user_accounts = relationship("Accounts", back_populates="user")
    user_contacts = relationship("Contacts", back_populates="user")


class Contacts(Base):
    __tablename__ = "contacts"
    user_username = Column(String(length=25),ForeignKey('users.username'), index=True) # ForeignKey ; here it is the user.username not user.id which we are using, isn't it?
    contact_username = Column(Integer,nullable=False) # Phone number?

    contacts_users = relationship("User", back_populates="contacts", foreign_keys=[user_username])


class Accounts(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(length=25), ForeignKey('users.username'), index=True, nullable=False) # ForeignKey
    balance = Column(Float, default=0.00, nullable=False)
    is_blocked = Column(Boolean, default=False, index=True)

    accounts_user = relationship("User", back_populates="accounts", foreign_keys=[username])
    acccounts_cards = relationship("Cards",back_populates="accounts")


class Cards(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False,) # ForeignKey
    card_number = Column(String(length=16), unique=True, index=True, nullable=False)
    expiration_date = Column(DateTime.datetime,index=True, nullable=False) # format in database 'YYYY-MM-DD HH:MM:SS'
    card_holder = Column(String(length=40),nullable=False)
    cvv = Column(String(length=3),nullable=False)
    design_path = Column(String(length=150)) # Nullable=False based on Front end?

    cards_accounts = relationship("Accounts", back_populates="cards")

class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_account = Column(Integer, index=True, nullable=False)
    receiver_account = Column(Integer, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False) # ForeignKey 
    description = Column(Text)
    transaction_date = Column(DateTime,default=None) # Autopopulates when it is completed.
    status = Column(Integer, nullable=False) # int value (0 = pending, 1 = completed, 2 = declined)
    is_recurring = Column(Boolean,default=False, nullable=False) 
    recurring_interval = Column(Integer) # int value (0 = daily, 1 = weekly, 2 = monthly)
    is_flagged = Column(Integer, nullable=False)


class Categories(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(length=30), nullable=False)
    color = Column(String(length=20)) # We can have predefined colours. How do we store them as a data type?

    categories_transactions = relationship("Transactions", backref="categories")


