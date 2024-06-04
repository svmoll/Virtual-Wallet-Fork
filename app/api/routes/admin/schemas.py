from pydantic import BaseModel


class UsersfrimlistDTO(BaseModel):
    username: str
    email: str
    password: str