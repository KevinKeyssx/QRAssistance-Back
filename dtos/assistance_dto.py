from pydantic       import BaseModel, Field
from datetime       import datetime
from typing         import Optional
from .member_dto    import MemberReadDTO
from .qr_dto        import QRReadDTO


class AssistanceCreateDTO( BaseModel ):
    member_id   : str
    qr_id       : str


class AssistanceReadDTO( BaseModel ):
    id          : str = Field( ..., alias="_id" )
    member      : MemberReadDTO
    qr          : QRReadDTO
    created_at  : datetime

    class Config:
        populate_by_name = True
