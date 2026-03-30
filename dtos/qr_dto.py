from pydantic           import BaseModel, Field
from datetime           import datetime
from typing             import Optional, List
from entities.qr        import QRType
from dtos.paginated_dto import PaginatedResponse


class QRCreateDTO(BaseModel):
    type        : QRType    = Field(..., description="Tipo de QR")
    date        : datetime  = Field(..., description="Fecha del QR")
    start_hour  : str       = Field(..., min_length = 5, max_length = 5, example = "09:00", description="Hora de inicio del QR")
    end_hour    : str       = Field(..., min_length = 5, max_length = 5, example = "10:30", description="Hora de fin del QR")


class QRUpdateDTO(BaseModel):
    type        : Optional[QRType]      = Field(None, description="Tipo de QR")
    date        : Optional[datetime]    = Field(None, description="Fecha del QR")
    start_hour  : Optional[str]         = Field(None, min_length = 5, max_length = 5, description="Hora de inicio del QR")
    end_hour    : Optional[str]         = Field(None, min_length = 5, max_length = 5, description="Hora de fin del QR")


class QRReadDTO( QRCreateDTO ):
    id: str = Field(..., alias="_id", description="ID del QR")
    created_at: datetime = Field(..., description="Fecha de creación del QR")
    updated_at: datetime = Field(..., description="Fecha de actualización del QR")

    class Config:
        populate_by_name = True
        from_attributes = True


class QRWithCountDTO( QRReadDTO ):
    assist_count: int = Field(0, description="Cantidad de asistencias del QR")


class PaginatedQRResponse( PaginatedResponse[QRWithCountDTO] ):
    pass
