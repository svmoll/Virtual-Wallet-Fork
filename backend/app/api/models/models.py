# Database models
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Date,
    DECIMAL,
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=25), unique=True, nullable=False)
    password = Column(String(length=200), nullable=False)
    email = Column(String(length=50), unique=True, nullable=False)
    phone_number = Column(String(length=100), unique=True, nullable=False)
    photo_path = Column(String(length=300))
    is_admin = Column(Boolean, default=False, nullable=False)
    is_restricted = Column(Boolean, default=False, nullable=False)

    user_accounts = relationship("Account", back_populates="accounts_user")

    contacts_as_user = relationship(
        "Contact", foreign_keys="[Contact.user_username]", back_populates="user"
    )
    contacts_as_contact = relationship(
        "Contact",
        foreign_keys="[Contact.contact_username]",
        back_populates="contact_user",
    )


class Contact(Base):
    __tablename__ = "contacts"
    user_username = Column(
        String(length=25), ForeignKey("users.username"), primary_key=True
    )
    contact_username = Column(
        String(length=25),
        ForeignKey("users.username"),
        primary_key=True,
    )

    user = relationship(
        "User", foreign_keys=[user_username], back_populates="contacts_as_user"
    )
    contact_user = relationship(
        "User", foreign_keys=[contact_username], back_populates="contacts_as_contact"
    )


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(
        String(length=25), ForeignKey("users.username"), nullable=False
    )  # ForeignKey
    balance = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    is_blocked = Column(Boolean, default=False)

    accounts_user = relationship(
        "User", back_populates="user_accounts", foreign_keys=[username]
    )
    accounts_cards = relationship("Card", back_populates="cards_accounts")


class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False,
    )  # ForeignKey
    card_number = Column(String(length=16), unique=True, nullable=False)
    expiration_date = Column(Date, nullable=False)
    card_holder = Column(String(length=50), nullable=False)
    cvv = Column(String(length=3), nullable=False)
    design_path = Column(String(length=150))

    cards_accounts = relationship("Account", back_populates="accounts_cards")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_account = Column(Integer, nullable=False)
    receiver_account = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text)
    transaction_date = Column(DateTime, default=None)
    status = Column(
        Integer, nullable=False, default=0
    )  # (0 = pending, 1 = completed, 2 = declined)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_interval = Column(Integer)  # (0 = daily, 1 = weekly, 2 = monthly)
    is_flagged = Column(Boolean, default=False, nullable=False)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=30), nullable=False)
    color_hex = Column(String(length=7), nullable=False)

    categories_transactions = relationship("Transaction", backref="categories")
