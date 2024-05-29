from datetime import datetime, date
from typing import Any
from dataclasses import dataclass, fields
from decimal import Decimal

from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Date,
    DECIMAL,
)
from decimal import Decimal
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm.decl_api import Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from dataclasses import dataclass

Base = declarative_base()


@dataclass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(length=25), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(length=200), nullable=False)
    email: Mapped[str] = mapped_column(String(length=50), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(
        String(length=100), unique=True, nullable=False
    )
    fullname: Mapped[str] = mapped_column(String(length=30), nullable=False)
    photo_path: Mapped[str] = mapped_column(String(length=300), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contacts_as_user = relationship(
        "Contact", foreign_keys="[Contact.user_username]", back_populates="user"
    )
    contacts_as_contact = relationship(
        "Contact",
        foreign_keys="[Contact.contact_username]",
        back_populates="contact_user",
    )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, User):
            return False
        return all(
            getattr(self, field.name) == getattr(other, field.name)
            for field in fields(self)
        )


@dataclass
class Contact(Base):
    __tablename__ = "contacts"
    user_username: Mapped[str] = mapped_column(
        String(length=25), ForeignKey("users.username"), primary_key=True
    )
    contact_username: Mapped[str] = mapped_column(
        String(length=25), ForeignKey("users.username"), primary_key=True
    )

    user = relationship(
        "User", foreign_keys=[user_username], back_populates="contacts_as_user"
    )
    contact_user = relationship(
        "User", foreign_keys=[contact_username], back_populates="contacts_as_contact"
    )


@dataclass
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(length=25), ForeignKey("users.username"), nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), default=0.00, nullable=False
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    accounts_cards = relationship("Card", back_populates="cards_accounts")

    sent_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.sender_account]",
        back_populates="sender_account_rel",
    )

    received_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.receiver_account]",
        back_populates="receiver_account_rel",
    )

    @hybrid_property
    def all_transactions(self):
        return self.sent_transactions + self.received_transactions


@dataclass
class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )
    card_number: Mapped[str] = mapped_column(
        String(length=16), unique=True, nullable=False
    )
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
    card_holder: Mapped[str] = mapped_column(String(length=50), nullable=False)
    cvv: Mapped[str] = mapped_column(String(length=3), nullable=False)
    design_path: Mapped[str] = mapped_column(String(length=150), nullable=True)

    cards_accounts = relationship("Account", back_populates="accounts_cards")


@dataclass
class BaseTransaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    sender_account: Mapped[str] = mapped_column(
        String(length=25), ForeignKey("accounts.username"), nullable=False
    )
    receiver_account: Mapped[str] = mapped_column(
        String(length=25), ForeignKey("accounts.username"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime, default=None, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(length=10), default="draft", nullable=False
    )  # (other statuses: "pending", "completed", "declined")
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    type: Mapped[str] = mapped_column(String(length=50))

    __mapper_args__ = {"polymorphic_identity": "transaction", "polymorphic_on": type}

    sender_account_rel = relationship(
        "Account", foreign_keys=[sender_account], back_populates="sent_transactions"
    )
    receiver_account_rel = relationship(
        "Account",
        foreign_keys=[receiver_account],
        back_populates="received_transactions",
    )


@dataclass
class Transaction(BaseTransaction):
    __mapper_args__ = {
        "polymorphic_identity": "transaction",
    }

    def __init__(
        self,
        sender_account,
        receiver_account,
        amount,
        category_id=None,
        description=None,
        transaction_date=None,
        status="draft",
        is_flagged=False,
        id=None,  # for testing purposes; needs to be resolved
    ):
        self.sender_account = sender_account
        self.receiver_account = receiver_account
        self.amount = amount
        self.category_id = category_id
        self.description = description
        self.transaction_date = transaction_date
        self.status = status
        self.is_flagged = is_flagged
        if id is not None:
            self.id = id  # for testing purposes, needs to be resolved

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Transaction):
            return False
        return all(
            getattr(self, field.name) == getattr(other, field.name)
            for field in fields(self)
        )


@dataclass
class RecurringTransaction(BaseTransaction):
    recurring_interval: Mapped[int] = mapped_column(
        Integer, default=None, nullable=True
    )  # (0 = daily, 1 = weekly, 2 = monthly)

    __mapper_args__ = {
        "polymorphic_identity": "recurring_transaction",
    }

    def __init__(
        self,
        sender_account,
        receiver_account,
        amount,
        category_id=None,
        description=None,
        transaction_date=None,
        recurring_interval=None,
        status="draft",
        is_flagged=False,
        id=None,  # for testing purposes; needs to be resolved
    ):
        self.sender_account = sender_account
        self.receiver_account = receiver_account
        self.amount = amount  # Decimal(f"{amount:.2f}")
        self.category_id = category_id
        self.description = description
        self.transaction_date = transaction_date
        self.status = status
        self.recurring_interval = recurring_interval
        self.is_flagged = is_flagged
        if id is not None:
            self.id = id  # for testing purposes, needs to be resolved


@dataclass
class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    color_hex: Mapped[str] = mapped_column(String(length=7), nullable=False)

    categories_transactions = relationship("Transaction", backref="categories")
