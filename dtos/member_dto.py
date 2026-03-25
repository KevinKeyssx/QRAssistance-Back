from pydantic   import BaseModel, Field
from typing     import List, Optional
from datetime   import datetime

# DTOs
from dtos.paginated_dto import PaginatedResponse


class MemberCreateDTO(BaseModel):
    name        : str = Field(..., min_length=2)
    last_name   : str = Field(..., min_length=2)
    classes     : List[str] = []
    ulid_token  : str = Field(..., description="Token ULID único del miembro")
    saveFinger  : bool = False


class MemberUpdateDTO(BaseModel):
    name        : Optional[str]         = None
    last_name   : Optional[str]         = None
    classes     : Optional[List[str]]   = None
    ulid_token  : Optional[str]         = None
    saveFinger  : Optional[bool]        = None


class MemberReadDTO(MemberCreateDTO):
    id          : str = Field(..., alias="_id")
    created_at  : datetime
    updated_at  : datetime

    class Config:
        populate_by_name    = True
        from_attributes     = True


class PaginatedMemberResponse( PaginatedResponse[ MemberReadDTO ]):
    pass
