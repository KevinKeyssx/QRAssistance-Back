from pydantic           import BaseModel, Field
from datetime           import datetime
from typing             import Optional

# DTOs
from dtos.member_dto    import MemberReadDTO
from dtos.qr_dto        import QRReadDTO
from dtos.paginated_dto import PaginatedResponse


class SurveyCreateDTO( BaseModel ):
    member_ulid   : str  = Field( ..., description="ULID del miembro" )
    qr_session_id : str  = Field( ..., description="Session ID del QR" )
    question1     : bool = Field( default=False, description="Respuesta pregunta 1" )
    question2     : bool = Field( default=False, description="Respuesta pregunta 2" )
    question3     : bool = Field( default=False, description="Respuesta pregunta 3" )
    question4     : bool = Field( default=False, description="Respuesta pregunta 4" )


# class SurveyUpdateDTO( BaseModel ):
#     question1 : Optional[bool] = Field( None, description="Respuesta pregunta 1" )
#     question2 : Optional[bool] = Field( None, description="Respuesta pregunta 2" )
#     question3 : Optional[bool] = Field( None, description="Respuesta pregunta 3" )
#     question4 : Optional[bool] = Field( None, description="Respuesta pregunta 4" )


class SurveyReadDTO( BaseModel ):
    id         : str          = Field( ..., alias="_id", description="ID de la encuesta" )
    member     : MemberReadDTO
    qr         : QRReadDTO
    question1  : bool
    question2  : bool
    question3  : bool
    question4  : bool
    created_at : datetime
    updated_at : datetime

    class Config:
        populate_by_name = True
        from_attributes  = True


class PaginatedSurveyResponse( PaginatedResponse[ SurveyReadDTO ] ):
    pass
