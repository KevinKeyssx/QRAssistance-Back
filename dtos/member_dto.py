from pydantic   import BaseModel, Field
from typing     import List, Optional
from datetime   import datetime

# DTOs
from dtos.paginated_dto import PaginatedResponse


class MemberCreateDTO( BaseModel ):
    name        : str       = Field(..., min_length=2, max_length=50, description="Nombre del miembro")
    last_name   : str       = Field(..., min_length=2, max_length=50, description="Apellido del miembro")
    classes     : List[str] = Field(default_factory=list, description="Clases del miembro")
    saveFinger  : bool      = Field(default=False, description="Indica si se debe guardar la huella digital del miembro")


class MemberUpdateDTO( BaseModel ):
    name        : Optional[str]         = Field(None, min_length=2, max_length=50, description="Nombre del miembro")
    last_name   : Optional[str]         = Field(None, min_length=2, max_length=50, description="Apellido del miembro")
    classes     : Optional[List[str]]   = Field(None, description="Clases del miembro")
    saveFinger  : Optional[bool]        = Field(None, description="Indica si se debe guardar la huella digital del miembro")


class MemberReadDTO( MemberCreateDTO ):
    id          : str = Field( ..., alias = "_id" )
    ulid_token  : str 
    created_at  : datetime
    updated_at  : datetime

    class Config:
        populate_by_name    = True
        from_attributes     = True


class PaginatedMemberResponse( PaginatedResponse[ MemberReadDTO ]):
    pass
