from beanie     import Document
from pydantic   import Field
from ulid       import ULID
from datetime   import datetime
from typing     import List


class Member( Document ):
    id          : str       = Field( default_factory = lambda: str( ULID() ), alias = "_id" )
    name        : str       = Field( ..., min_length = 2, max_length = 50 )
    last_name   : str       = Field( ..., min_length = 2, max_length = 50 )
    classes     : List[str] = Field( default_factory = list )
    ulid_token  : str       = Field( default_factory = lambda: str( ULID() ) )
    saveFinger  : bool      = Field( default = False )

    created_at  : datetime  = Field( default_factory = datetime.utcnow )
    updated_at  : datetime  = Field( default_factory = datetime.utcnow )

    class Settings:
        name = "members"
