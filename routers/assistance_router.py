from fastapi    import APIRouter, status, HTTPException, status, Response
import pytz

# Env
import os
from dotenv import load_dotenv

# Datetime
from datetime   import datetime, time

# Typing
from typing     import List, Union

# DTO
from dtos.assistance_dto    import AssistanceCreateDTO, AssistanceReadDTO
from dtos.member_dto        import MemberReadDTO

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
    member  = await Member.find_one( Member.ulid_token == data.member_ulid )
    qr      = await QR.find_one( QR.session_id == data.qr_session_id )

    if not member or not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = {
                "code"    : ErrorCode.ERR_103,
                "message" : f"Miembro o QR no encontrado."
            }
        )

    # 1. Validamos que el miembro pueda asistir a esta clase
    if qr.type not in member.classes:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = {
                "code"    : ErrorCode.ERR_201,
                "message" : "El miembro no puede asistir a esta clase."
            }
        )

    # 2. Obtener hora actual en la zona horaria configurada
    chile_tz        = pytz.timezone( TIMEZONE )
    now_local       = datetime.now( chile_tz )
    current_date    = now_local.date()
    current_time    = now_local.time()

    # 2.1 Validamos que el miembro no se ha registrado
    if await assistance_services.get_assistance_by_member_ulid_and_qr_session_id( data ):
        response.status_code = status.HTTP_200_OK
        return member

    # 3. Validar tercer domingo del mes
    # El tercer domingo ocurre cuando: weekday() == 6 (domingo) y el día está entre 15 y 21
    is_third_sunday = current_date.weekday() == 6 and 15 <= current_date.day <= 21

    if is_third_sunday:
        survey = await survey_services.get_survey_by_member_and_qr( member, qr )

        if not survey:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = {
                    "code"    : ErrorCode.ERR_301,
                    "message" : "Debes completar la encuesta del tercer domingo antes de registrar asistencia."
                }
            )

    # 3.1 Validar Fechas expiradas
    if qr.date.date() < current_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = {
                "code"    : ErrorCode.ERR_202,
                "message" : "Este QR ya expiró."
            }
        )

    # 3.2 Validar Fechas futuras
    if qr.date.date() > current_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = {
                "code"    : ErrorCode.ERR_203,
                "message" : f"Este QR es para la fecha {qr.date.date()}, no para hoy."
            }
        )

    # 4. Validar Rango Horario
    try:
        start_h, start_m    = map( int, qr.start_hour.split( ":" ) )
        end_h, end_m        = map( int, qr.end_hour.split( ":" ) )

        start_time  = time( start_h, start_m )
        end_time    = time( end_h, end_m )
    except ValueError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = {
                "code"    : ErrorCode.ERR_205,
                "message" : "Formato de hora en QR inválido."
            }
        )

    if start_time <= end_time:
        is_in_range = start_time <= current_time <= end_time
    else:
        is_in_range = current_time >= start_time or current_time <= end_time

    if not is_in_range:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = {
                "code"    : ErrorCode.ERR_204,
                "message" : f"Fuera de horario. Válido de {qr.start_hour} a {qr.end_hour}. Hora actual: {current_time.strftime('%H:%M')}."
            }
        )

    # 5. Registramos asistencia
    assistance = await assistance_services.register_assistance( member, qr )

    if not assistance:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = {
                "code"    : ErrorCode.ERR_501,
                "message" : "Error al registrar la asistencia."
            }
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
