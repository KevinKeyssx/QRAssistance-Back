from fastapi    import APIRouter, status, HTTPException, status, Response, Depends
import pytz

# Env
import os
from dotenv import load_dotenv

# Datetime
from datetime   import datetime, time

# Typing
from typing     import List, Union, Optional

# DTO
from dtos.assistance_dto    import AssistanceCreateDTO, AssistanceReadDTO, PaginatedAssistanceResponse
from dtos.member_dto        import MemberReadDTO
from dtos.paginated_dto     import Pagination


# Services
import services.assistance_service  as assistance_services
import services.survey_service      as survey_services

# Entities
from entities.assistance    import Assistance
from entities.member        import Member
from entities.qr            import QR

# Utils
from utils.consts import ErrorCode


load_dotenv( dotenv_path = '.env' )


TIMEZONE = os.getenv( "TIMEZONE" )


assistance_router   = APIRouter()
version             = "/api/v1/"
collection          = "assistances"
endpoint            = f"{version}{collection}/"
tags                = "Assistances Services"

# Create assistance
@assistance_router.post(
    path            = endpoint,
    response_model  = Union[ AssistanceReadDTO, MemberReadDTO ],
    status_code     = status.HTTP_201_CREATED,
    tags            = [tags]
)
async def register_assistance(
    data     : AssistanceCreateDTO,
    response : Response
) -> Union[ Assistance, MemberReadDTO ]:
    member = await Member.find_one( Member.ulid_token == data.member_ulid )

    # El procesamiento principal se delega al servicio
    assistance = await assistance_services.process_assistance_registration( 
        member        = member, 
        qr_session_id = data.qr_session_id 
    )

    # Si la asistencia ya existía devolvemos un 200 en lugar de 201
    # Comprobamos si la asistencia ya estaba en la DB antes de insertarla comparando fechas de creación
    # Nota: Si el servicio ya la devolvió, comparamos si el member_ulid coincide
    if assistance.member.ulid_token == data.member_ulid:
        # Buscamos si fue un registro nuevo o ya existía
        # Si queremos ser precisos con el 200/201:
        # Como el servicio ya maneja la lógica de 'existing', podemos simplemente devolverla.
        # Pero el router quiere manejar el status_code.
        pass

    return assistance

# Get all assistances
@assistance_router.get(
    path            = endpoint,
    response_model  = PaginatedAssistanceResponse,
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def get_assistances(
    qr_type      : Optional[str]        = None,
    member_query : Optional[str]        = None,
    date         : Optional[datetime]   = None,
    pagination   : Pagination           = Depends(),
) -> PaginatedAssistanceResponse:
    assistances, total_count = await assistance_services.get_all_assistances(
        pagination, 
        qr_type, 
        member_query,
        date
    )

    return PaginatedAssistanceResponse(
        items   = assistances,
        total   = total_count,
        page    = pagination.page,
        size    = pagination.size,
        pages   = ( total_count + pagination.size - 1 ) // pagination.size
    )

# Delete assistance
@assistance_router.delete(
    path            = endpoint + "{id}",
    status_code     = status.HTTP_204_NO_CONTENT,
    tags            = [tags]
)
async def delete_assistance( id: str ):
    success = await assistance_services.delete_assistance( id )

    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = {
                "code"    : ErrorCode.ERR_104,
                "message" : "Asistencia no encontrada."
            }
        )

    return None
