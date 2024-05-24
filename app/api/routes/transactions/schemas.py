from pydantic import BaseModel


class TransactionDTO(BaseModel):
    receiver_account: str
    amount: float
