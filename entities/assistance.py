from beanie             import Document, Link
from pydantic           import Field
from ulid               import ULID
from datetime           import datetime
from entities.member    import Member
from entities.qr        import QR


class Assistance( Document ):
    id          : str       = Field( default_factory=lambda: str(ULID()), alias="_id" )

    member      : Link[Member]
    qr          : Link[QR]

    created_at  : datetime    = Field( default_factory=datetime.utcnow )
    updated_at  : datetime    = Field( default_factory=datetime.utcnow )

    class Settings:
        name = "assistances"
