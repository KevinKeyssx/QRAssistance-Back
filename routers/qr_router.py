# Python
from typing import List

# Services
import services.qr_service as qr_services

# Model
from entities.qr import QR

# FastApi
from fastapi import Body, status, APIRouter, Path, HTTPException, Query, Depends

# DTOs
from dtos.qr_dto import QRCreateDTO, QRReadDTO, QRUpdateDTO, QRWithCountDTO, PaginatedQRResponse
from dtos.paginated_dto import Pagination

# Variables
qr_router   = APIRouter()
version     = "/api/v1/"
collection  = "qrs"
endpoint    = version + collection + "/"
tags        = "QR Services"

# Read all QRs
@qr_router.get(
    path            = endpoint,
    response_model  = PaginatedQRResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "Obtiene QRs paginados del año actual.",
    tags            = [tags]
)
async def get_all_qrs(
    pagination: Pagination = Depends(),
    year: int = Query(
        None,
        ge          = 1900,
        le          = 2100,
        description = "Año"
    )
) -> PaginatedQRResponse:
    """
    ## Lista QRs con paginación.
    Filtra automáticamente los QRs que pertenecen al año actual.
    """
    return await qr_services.get_all_qrs_with_stats(
        page = pagination.page,
        size = pagination.size,
        year = year
    )

# Create QR
@qr_router.post(
    path            = endpoint,
    response_model  = QRReadDTO,
    status_code     = status.HTTP_201_CREATED,
    tags            = [tags]
)
async def create_qr(
    qr_in: QRCreateDTO = Body(...)
) -> QRReadDTO:
    new_qr = QR( **qr_in.model_dump() )

    return await qr_services.create_qr( new_qr )

# Read QR by ID
@qr_router.get(
    path            = f"{endpoint}{{qr_id}}",
    response_model  = QRReadDTO,
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def read_qr(
    qr_id: str = Path( ..., description="El ID del QR a buscar" )
) -> QRReadDTO:
    qr = await qr_services.get_qr_by_id( qr_id )

    if not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "QR no encontrado"
        )

    return qr

# Update QR
@qr_router.put(
    path            = f"{endpoint}{{qr_id}}",
    response_model  = QRReadDTO,
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def update_qr(
    qr_in: QRUpdateDTO = Body(...),
    qr_id: str = Path(
        ...,
        description="El ID del QR a actualizar")
) -> QRReadDTO:
    updated_qr = await qr_services.update_qr( qr_id, qr_in.model_dump( exclude_unset=True ))

    if not updated_qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "QR no encontrado"
        )

    return updated_qr

# Delete QR
@qr_router.delete(
    path            = f"{endpoint}{{qr_id}}",
    status_code     = status.HTTP_204_NO_CONTENT,
    tags            = [tags]
)
async def delete_qr(
    qr_id: str = Path( ..., description="El ID del QR a eliminar" )
) -> None:
    deleted = await qr_services.delete_qr( qr_id )

    if not deleted:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "QR no encontrado"
        )

    return None
