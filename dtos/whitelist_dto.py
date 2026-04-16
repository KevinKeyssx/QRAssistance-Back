from pydantic       import BaseModel, Field, EmailStr
from datetime       import datetime


validateEmail = {
    "pattern"     : r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "min_length"  : 5,
    "max_length"  : 250,
    "description" : "Email del usuario",
    "examples"    : [ "user@example.com" ]
}


class WhiteListCreateDTO( BaseModel ):
    email : str = Field( ..., **validateEmail )


class WhiteListReadDTO( BaseModel ):
    id          : str
    email       : str
    created_at  : datetime
    updated_at  : datetime

    class Config:
        populate_by_name = True
        from_attributes  = True
