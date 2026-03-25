from pydantic           import BaseModel, Field
from datetime           import datetime
from typing             import Optional, List
from entities.qr        import QRType
from dtos.paginated_dto import PaginatedResponse


class QRCreateDTO(BaseModel):
    type        : QRType
    date        : datetime
    start_hour  : str = Field( ..., min_length = 5, max_length = 5, example = "09:00" )
    end_hour    : str = Field( ..., min_length = 5, max_length = 5, example = "10:30" )


class QRUpdateDTO(BaseModel):
    type        : Optional[QRType]      = None
    date        : Optional[datetime]    = None
    start_hour  : Optional[str]         = Field( None, min_length = 5, max_length = 5 )
    end_hour    : Optional[str]         = Field( None, min_length = 5, max_length = 5 )


class QRReadDTO( QRCreateDTO ):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class QRWithCountDTO( QRReadDTO ):
    assist_count: int = 0


class PaginatedQRResponse( PaginatedResponse[QRWithCountDTO] ):
    pass
