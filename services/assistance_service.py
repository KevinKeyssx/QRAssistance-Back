# MongoDB
from beanie     import init_beanie, Link
from beanie.operators import In
from database   import db

# Python
import os
import pytz
from typing import List, Optional, Tuple, Union
from datetime   import datetime, time

# FastApi
from fastapi import status, HTTPException

# Entities
from entities.assistance    import Assistance
from entities.member        import Member
from entities.qr            import QR

# Dtos
from dtos.assistance_dto    import AssistanceCreateDTO
from dtos.paginated_dto     import Pagination

# Services
import services.survey_service as survey_services

# Utils
from utils.consts import ErrorCode


async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ Assistance ]
	)


async def register_assistance(
    member  : Member,
    qr      : QR
) -> Assistance:
    if not member or not qr:
        return None

    new_assistance = Assistance( member = member, qr = qr )

    return await new_assistance.insert()


async def get_all_assistances(
    pagination      : Pagination,
    qr_type         : Optional[str]         = None,
    member_query    : Optional[str]         = None,
    date            : Optional[datetime]    = None
) -> Tuple[List[Assistance], int]:
    # 1. Preparar lista de expresiones de filtrado de Beanie
    expressions = []

    if member_query:
        # Buscamos miembros que coincidan con el nombre o apellido
        matching_members = await Member.find({
            "$or": [
                { "name"        : { "$regex": member_query, "$options": "i" } },
                { "last_name"   : { "$regex": member_query, "$options": "i" } }
            ]
        }).to_list()
        
        member_ids = [ m.id for m in matching_members ]
        expressions.append( In( Assistance.member.id, member_ids ) )

    if date:
        start_of_day = date.replace( hour = 0, minute = 0, second = 0, microsecond = 0 )
        end_of_day   = date.replace( hour = 23, minute = 59, second = 59, microsecond = 999999 )
        expressions.append( Assistance.created_at >= start_of_day )
        expressions.append( Assistance.created_at <= end_of_day )

    if qr_type:
        matching_qrs = await QR.find( QR.type == qr_type ).to_list()
        qr_ids       = [ q.id for q in matching_qrs ]
        expressions.append( In( Assistance.qr.id, qr_ids ) )

    # 2. Ejecutar consulta usando expresiones nativas
    query       = Assistance.find( *expressions, fetch_links = True )
    total_count = await query.count()

    # 3. Ejecución de la paginación y obtención de resultados
    assistances = await query.skip(
        ( pagination.page - 1 ) * pagination.size
    ).limit( pagination.size ).to_list()

    # Filtrado final de seguridad opcional (Beanie con fetch_links ya lo maneja internamente)
    result = [ a for a in assistances if a.member is not None and a.qr is not None ]

    return result, total_count


async def get_assistance_by_member_ulid_and_qr_session_id(
    data: AssistanceCreateDTO
) -> Assistance:
    return await Assistance.find_one(
        Assistance.member.ulid_token == data.member_ulid,

        Assistance.qr.session_id == data.qr_session_id,

        fetch_links = True
    )


async def delete_assistance( id: str ) -> bool:
    assistance = await Assistance.get( id )

    if assistance:
        await assistance.delete()
        return True

    return False


async def process_assistance_registration( 
    member        : Member, 
    qr_session_id : str 
) -> Assistance:
    """
    Procesa el registro de una asistencia validando todas las reglas de negocio.
    Lanza HTTPException si alguna validación falla.
    """
    member  = await Member.find_one( Member.ulid_token == member.ulid_token )
    qr      = await QR.find_one( QR.session_id == qr_session_id )

    if not member or not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = {
                "code"    : ErrorCode.ERR_103,
                "message" : "Miembro o QR no encontrado."
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
    timezone_env    = os.getenv( "TIMEZONE", "America/Santiago" )
    chile_tz        = pytz.timezone( timezone_env )
    now_local       = datetime.now( chile_tz )
    current_date    = now_local.date()
    current_time    = now_local.time()

    # 2.1 Validamos si ya existe la asistencia
    existing = await get_assistance_by_member_ulid_and_qr_session_id(
        AssistanceCreateDTO( member_ulid = member.ulid_token, qr_session_id = qr_session_id )
    )
    if existing:
        return existing

    # 3. Validar tercer domingo del mes
    # is_third_sunday = current_date.weekday() == 6 and 15 <= current_date.day <= 21

    # if is_third_sunday:
    #     survey = await survey_services.get_survey_by_member_and_qr( member, qr )

    #     if not survey:
    #         raise HTTPException(
    #             status_code = status.HTTP_400_BAD_REQUEST,
    #             detail      = {
    #                 "code"    : ErrorCode.ERR_301,
    #                 "message" : "Debes completar la encuesta del tercer domingo antes de registrar asistencia."
    #             }
    #         )

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
                "message" : f"Este QR es para la fecha { qr.date.date() }, no para hoy."
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
                "message" : f"Fuera de horario. Válido de { qr.start_hour } a { qr.end_hour }. Hora actual: { current_time.strftime( '%H:%M' ) }."
            }
        )

    # 5. Registramos asistencia
    assistance = await register_assistance( member, qr )

    if not assistance:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = {
                "code"    : ErrorCode.ERR_501,
                "message" : "Error al registrar la asistencia."
            }
        )

    return assistance
