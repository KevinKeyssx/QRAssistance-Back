from pydantic       import BaseModel, Field
from datetime       import datetime
from typing         import Optional

# DTOs
from dtos.paginated_dto import PaginatedResponse
from .member_dto        import MemberReadDTO
from .qr_dto            import QRReadDTO


class AssistanceCreateDTO( BaseModel ):
    member_ulid     : str = Field( ..., description="ULID del miembro" )
    qr_session_id   : str = Field( ..., description="ID de la sesión del QR" )


class AssistanceReadDTO( BaseModel ):
    id          : str           = Field( ..., alias="_id", description="ID de la asistencia" )
    member      : MemberReadDTO = Field( ..., description="Miembro que asistió" )
    qr          : QRReadDTO     = Field( ..., description="QR al que asistió" )
    created_at  : datetime      = Field( ..., description="Fecha de creación de la asistencia" )
    updated_at  : datetime      = Field( ..., description="Fecha de actualización de la asistencia" )

    class Config:
        populate_by_name = True
        from_attributes  = True


class PaginatedAssistanceResponse( PaginatedResponse[ AssistanceReadDTO ]):
    pass
