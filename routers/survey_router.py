# Python
import os
import pytz
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Services
import services.survey_service as survey_services

# Model
from entities.survey import Survey

# FastApi
from fastapi import Body, status, APIRouter, Path, HTTPException, Query, Depends

# DTOs
from dtos.survey_dto    import SurveyCreateDTO, SurveyReadDTO, SurveyUpdateDTO, SurveyWithCountDTO, PaginatedSurveyResponse
from dtos.paginated_dto import Pagination


load_dotenv( dotenv_path = '.env' )


TIMEZONE = os.getenv( "TIMEZONE" )

# Variables
qr_router   = APIRouter()
version     = "/api/v1/"
collection  = "surveys"
endpoint    = version + collection + "/"
tags        = "Survey Services"

# Read all QRs
@qr_router.get(
    path            = endpoint,
    response_model  = PaginatedQRResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "Obtiene las encuentas paginados mensual y/o anual.",
    tags            = [tags]
)
async def get_all_surveys(
    pagination: Pagination = Depends(),
    year: int = Query(
        None,
        ge          = 2026,
        le          = 2100,
        description = "Año"
    )
) -> PaginatedQRResponse:
    """
    ## Lista QRs con paginación.
    Filtra automáticamente los QRs que pertenecen al año actual.
    """
    return await survey_services.get_all_surveys_with_stats(
        page = pagination.page,
        size = pagination.size,
        year = year
    )
