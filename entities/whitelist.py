from beanie         import Document
from pydantic       import Field
from ulid           import ULID
from datetime       import datetime


class WhiteList( Document ):
    id          : str       = Field( default_factory=lambda: str(ULID()), alias="_id" )
    email       : str       = Field( ..., min_length = 5, max_length = 250 )

    created_at  : datetime  = Field( default_factory=datetime.utcnow )
    updated_at  : datetime  = Field( default_factory=datetime.utcnow )

    class Settings:
        name = "whitelist"
