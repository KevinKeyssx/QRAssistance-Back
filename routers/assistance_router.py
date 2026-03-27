from fastapi    import APIRouter, status, HTTPException, status
import pytz

# Env
import os
from dotenv import load_dotenv

# Datetime
from datetime   import datetime, time

# Typing
from typing     import List

# DTO
from dtos.assistance_dto import AssistanceCreateDTO, AssistanceReadDTO

# Services
import services.assistance_service as assistance_services

# Entities
from entities.assistance    import Assistance
from entities.member        import Member
from entities.qr            import QR


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
    response_model  = AssistanceReadDTO,
    status_code     = status.HTTP_201_CREATED,
    tags            = [tags]
)
async def register_assistance(data: AssistanceCreateDTO) -> Assistance:
    member  = await Member.find_one( Member.ulid_token == data.member_ulid )
    qr      = await QR.find_one( QR.session_id == data.qr_session_id )

    if not member or not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = f"Miembro o QR no encontrado {member} {qr}"
        )

    # 2. Obtener hora actual en UTC
    chile_tz        = pytz.timezone( TIMEZONE )
    now_utc         = datetime.now( chile_tz )
    current_date    = now_utc.date()
    current_time    = now_utc.time()

    if await assistance_services.get_assistance_by_member_ulid_and_qr_session_id( data ):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Ya registraste asistencia con este QR."
        )

    # 3.1 Validar Fechas expiradas
    if qr.date.date() < current_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Este QR ya expiró."
        )

    # 3.2 Validar Fechas futuras
    if qr.date.date() > current_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Este QR es para la fecha {qr.date.date()}, no para hoy."
        )

    # 4. Validar Rango Horario
    try:
        start_h, start_m    = map( int, qr.start_hour.split( ":" ))
        end_h, end_m        = map( int, qr.end_hour.split( ":" ))

        start_time  = time( start_h, start_m )
        end_time    = time( end_h, end_m )
    except ValueError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Formato de hora en QR inválido"
        )

    if start_time <= end_time:
        is_in_range = start_time <= current_time <= end_time
    else:
        is_in_range = current_time >= start_time or current_time <= end_time

    if not is_in_range:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Fuera de horario. Válido de {qr.start_hour} a {qr.end_hour}. Hora actual: {current_time.strftime('%H:%M')}"
        )

    # 5. Registramos asistencia
    assistance = await assistance_services.register_assistance( member, qr )

    if not assistance:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Miembro o QR no encontrado"
        )

    return assistance

# Get all assistances
@assistance_router.get(
    path            = endpoint,
    response_model  = List[AssistanceReadDTO],
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def get_assistances():
    return await assistance_services.get_all_assistances()

# Delete assistance
@assistance_router.delete(
    path            = endpoint + "{id}",
    status_code     = status.HTTP_204_NO_CONTENT,
    tags            = [tags]
)
async def delete_assistance(id: str):
    success = await assistance_services.delete_assistance(id)

    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Asistencia no encontrada"
        )

    return None
