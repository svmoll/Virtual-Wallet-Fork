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
        strip_whitespace=True, pattern=r'^{8,20}$') # TODO Find a Regex that works with pydantic and meets the cretaria for password
]


class UserDTO(BaseModel):
    id: int | None = None
    username: TUsername
    password: str
    email: Temail
    phone_number: str
    photo_url: str | None = None
    is_admin: bool = False
    is_restricted: bool = False

