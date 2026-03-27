from pydantic import BaseModel
from typing import List, Generic, TypeVar

from fastapi import Query

T = TypeVar("T")

class PaginatedResponse( BaseModel, Generic[T] ):
    items   : List[T]
    total   : int
    page    : int
    size    : int
    pages   : int


class Pagination( BaseModel ):
    page: int = Query(
        1,
        ge          = 1,
        le          = 1000000,
        description = "Número de página",
        examples    = [1]
    ),
    size: int = Query(
        10,
        ge          = 1,
        le          = 100,
        description = "Elementos por página"
    )