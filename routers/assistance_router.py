from fastapi    import APIRouter, status, HTTPException, status
from typing     import List
from datetime   import datetime, time

from dtos.assistance_dto import AssistanceCreateDTO, AssistanceReadDTO

import services.assistance_service as assistance_services


from entities.assistance import Assistance
from entities.member import Member
from entities.qr import QR

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
    # 1. Obtener datos
    member  = await Member.get( data.member_id )
    qr      = await QR.get( data.qr_id )

    if not member or not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Miembro o QR no encontrado"
        )

    # 2. Obtener hora actual en UTC
    now_utc         = datetime.utcnow()
    current_date    = now_utc.date()
    current_time    = now_utc.time()

    if await assistance_services.get_assistance_by_member_id_and_qr_id( data ):
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

    if not ( start_time <= current_time <= end_time ):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"Fuera de horario. Válido de {qr.start_hour} a {qr.end_hour}. Hora actual: {current_time.strftime('%H:%M')}"
        )

    # 5. Si todo está bien, registramos
    assistance = await assistance_services.register_assistance( data )

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
