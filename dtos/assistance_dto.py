from pydantic       import BaseModel, Field
from datetime       import datetime
from typing         import Optional
from .member_dto    import MemberReadDTO
from .qr_dto        import QRReadDTO


class AssistanceCreateDTO( BaseModel ):
    member_id   : str = Field( ..., description="ID del miembro" )
    qr_id       : str = Field( ..., description="ID del QR" )


class AssistanceReadDTO( BaseModel ):
    id          : str           = Field( ..., alias="_id", description="ID de la asistencia" )
    member      : MemberReadDTO = Field( ..., description="Miembro que asistió" )
    qr          : QRReadDTO     = Field( ..., description="QR al que asistió" )
    created_at  : datetime      = Field( ..., description="Fecha de creación de la asistencia" )

    class Config:
        populate_by_name = True
