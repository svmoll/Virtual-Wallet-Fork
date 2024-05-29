from pydantic import BaseModel
from decimal import Decimal

class AccountViewDTO(BaseModel):
    id: int
    username: str
    balance: Decimal
    _is_blocked: bool

    @property
    def is_blocked(self):
        return 1 if self._is_blocked else 0

    @is_blocked.setter
    def is_blocked(self, value):
        self._is_blocked = bool(value)

    @classmethod
    def from_query_result(cls, id: int, username: str, balance: Decimal, is_blocked: bool):
        return cls(id=id, username=username, balance=balance, is_blocked=is_blocked)

 

