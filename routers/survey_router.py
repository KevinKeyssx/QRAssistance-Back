# Python
import os
from datetime   import datetime
from typing     import List, Optional
from dotenv     import load_dotenv

# FastAPI
from fastapi    import APIRouter, status, HTTPException, Query

# Services
import services.survey_service as survey_services

# Entities
from entities.surveys   import Survey
from entities.member    import Member
from entities.qr        import QR

# DTOs
from dtos.survey_dto    import SurveyCreateDTO, SurveyReadDTO

# Utils
from utils.consts import ErrorCode


load_dotenv( dotenv_path = '.env' )


TIMEZONE = os.getenv( "TIMEZONE" )


survey_router   = APIRouter()
version         = "/api/v1/"
collection      = "surveys"
endpoint        = version + collection + "/"
tags            = "Survey Services"

# ── GET all surveys (year obligatorio, month opcional) ──────────────────────
@survey_router.get(
    path            = endpoint,
    response_model  = List[ SurveyReadDTO ],
    status_code     = status.HTTP_200_OK,
    summary         = "Obtiene las encuestas filtradas por año y opcionalmente por mes.",
    tags            = [tags]
)
async def get_all_surveys(
    year  : int = Query(
        ...,
        ge          = 2026,
        le          = 2100,
        description = "Año (obligatorio)"
    ),
    month : Optional[int] = Query(
        None,
        ge          = 1,
        le          = 12,
        description = "Mes (opcional, 1-12)"
    )
) -> List[ SurveyReadDTO ]:
    """
    ## Lista encuestas sin paginación.

    - **year** (obligatorio): filtra por año.
    - **month** (opcional): si se incluye, filtra por ese mes dentro del año dado.
    """
    return await survey_services.get_all_surveys( year=year, month=month )


# ── GET survey statistics ─────────────────────────────────────────────────────
@survey_router.get(
    path            = endpoint + "stats",
    status_code     = status.HTTP_200_OK,
    summary         = "Obtiene las estadísticas de las encuestas agregadas dinámicamente.",
    tags            = [tags]
)
async def get_survey_stats(
    year  : int = Query(
        ...,
        ge          = 2026,
        le          = 2100,
        description = "Año (obligatorio)"
    ),
    month : Optional[int] = Query(
        None,
        ge          = 1,
        le          = 12,
        description = "Mes (opcional, 1-12)"
    ),
    class_type: Optional[str] = Query(
        None,
        description = "Tipo de clase (opcional)"
    )
):
    """
    ## Retorna datos agregados de respuestas yes/no por cada clase y pregunta.
    """
    return await survey_services.get_survey_stats( year=year, month=month, class_type=class_type )


# ── POST create survey ────────────────────────────────────────────────────────
@survey_router.post(
    path            = endpoint,
    response_model  = SurveyReadDTO,
    status_code     = status.HTTP_201_CREATED,
    summary         = "Registra una nueva encuesta del tercer domingo.",
    tags            = [tags]
)
async def create_survey( data: SurveyCreateDTO ) -> SurveyReadDTO:
    """
    ## Crea una encuesta vinculada a un miembro y un QR.

    Si el miembro ya registró una encuesta para ese QR, retorna error **409**.
    """
    member  = await Member.find_one( Member.ulid_token == data.member_ulid )
    qr      = await QR.find_one( QR.session_id == data.qr_session_id )

    if not member or not qr:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = {
                "code"    : ErrorCode.ERR_103,
                "message" : "Miembro o QR no encontrado."
            }
        )

    existing = await survey_services.get_survey_by_member_and_qr( member, qr )

    if existing:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail      = {
                "code"    : ErrorCode.ERR_303,
                "message" : "El miembro ya registró una encuesta para este QR."
            }
        )

    survey = Survey(
        qr        = qr,
        member    = member,
        question1 = data.question1,
        question2 = data.question2,
        question3 = data.question3,
        question4 = data.question4
    )

    return await survey_services.create_survey( survey )
