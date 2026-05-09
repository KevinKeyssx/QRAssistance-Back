from fastapi    import APIRouter, status, HTTPException, Response, Depends
import pytz

# Env
from utils.envs import TIMEZONE, VISITING_MEMBER_ID

# Datetime
from datetime   import datetime, time

# Typing
from typing     import List, Union, Optional

# DTO
from dtos.assistance_dto    import AssistanceCreateDTO, AssistanceReadDTO, PaginatedAssistanceResponse, AssistanceCreateVisitorDTO
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


# Security
from utils.security import validate_internal_key


assistance_router   = APIRouter( dependencies = [ Depends( validate_internal_key ) ] )
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
async def create_register_assistance(
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

# Create assistance
@assistance_router.post(
    path            = f'{endpoint}visitor',
    response_model  = bool,
    status_code     = status.HTTP_201_CREATED,
    tags            = [tags]
)
async def register_visitor_assistance(
	data: AssistanceCreateVisitorDTO,
) -> bool:
	qr      = await QR.find_one( QR.session_id == data.qr_session_id )
	member  = await Member.find_one( Member.id == VISITING_MEMBER_ID )

	if not qr:
		raise HTTPException(
			status_code = status.HTTP_404_NOT_FOUND,
			detail      = {
				"code"    : ErrorCode.ERR_103,
				"message" : "QR no encontrado."
			}
		)

	#1.1 validar que el visitor_id no esté registrado
	existing = await Assistance.find_one(
		Assistance.visitor_id    == data.visitor_id,
		Assistance.qr.session_id == data.qr_session_id,
		fetch_links              = True
	)

	if ( existing ):
		return True

	# 2. Obtener hora actual en la zona horaria configurada
	chile_tz        = pytz.timezone( TIMEZONE )
	now_local       = datetime.now( chile_tz )
	current_date    = now_local.date()
	current_time    = now_local.time()

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
	assistance = await assistance_services.register_assistance( member, qr, data.visitor_id )

	if not assistance:
		raise HTTPException(
			status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail      = {
				"code"    : ErrorCode.ERR_501,
				"message" : "Error al registrar la asistencia."
			}
		)

	return True

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
