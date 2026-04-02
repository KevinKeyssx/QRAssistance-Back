from beanie             import Document, Link
from pydantic           import Field
from ulid               import ULID
from datetime           import datetime
from entities.qr        import QR


class Survey( Document ):
    id          : str       = Field( default_factory=lambda: str(ULID()), alias="_id" )

    qr          : Link[QR]
    question1   : bool  = Field( default=False )
    question2   : bool  = Field( default=False )
    question3   : bool  = Field( default=False )
    question4   : bool  = Field( default=False )

    created_at  : datetime  = Field( default_factory=datetime.utcnow )
    updated_at  : datetime  = Field( default_factory=datetime.utcnow )

    class Settings:
        name = "surveys"
