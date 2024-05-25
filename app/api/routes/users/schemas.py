from typing import Annotated

from pydantic import BaseModel, StringConstraints

TUsername = Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True, pattern=r"^\w{2,20}$")
]
Temail = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        pattern=r"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$",
    ),
]

TPassword = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, pattern=r"^{8,20}$"
    ),  # TODO Find a Regex that works with pydantic and meets the criteria for password
]

TPhoneNumber = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, pattern=r"^\d{10}$"
    )
]

class UserDTO(BaseModel):
    id: int | None = None
    username: TUsername
    password: str
    email: Temail
    phone_number: TPhoneNumber


class UserViewDTO(BaseModel):
    id: int
    username: str

    @classmethod
    def from_query_result(cls, id, username):
        return cls(id=id, username=username)

class UpdateUserDTO(BaseModel):
    password: str | None = None
    email: Temail | None = None
    phone_number: TPhoneNumber | None = None
    photo: str | None = None
