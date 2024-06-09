from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime


class TransactionDTO(BaseModel):
    receiver_account: str
    amount: Decimal
    category_id: int | None = None
    description: str | None = None


class RecurringTransactionDTO(TransactionDTO):
    recurring_interval: Literal[
        "daily", "weekly", "monthly", "yearly", "minute", "custom"
    ]
    custom_days: Optional[int] = Field(None, description="Custom interval in days")
    start_date: Optional[date] = Field(
        None, description="Start date for the recurring transaction"
    )


class RecurringTransactionView(BaseModel):
    id: int
    receiver: str
    amount: Decimal
    category_id: Optional[int] = None
    description: Optional[str]
    recurring_interval: str
    next_run_time: date
