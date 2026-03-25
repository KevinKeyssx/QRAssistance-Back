from beanie     import Document
from pydantic   import Field
from ulid       import ULID
from datetime   import datetime
from typing     import List


class Member( Document ):
    id          : str = Field( default_factory=lambda: str(ULID()), alias="_id" )
    name        : str
    last_name   : str
    classes     : List[str] = []
    ulid_token  : str
    saveFinger  : bool = False

    created_at  : datetime = Field( default_factory=datetime.utcnow )
    updated_at  : datetime = Field( default_factory=datetime.utcnow )

    class Settings:
        name = "members"
