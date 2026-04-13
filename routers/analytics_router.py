from fastapi    import APIRouter, status
from typing     import List, Optional

# DTO
from dtos.analytics_dto import (
    MainChartItemDTO, RetentionDTO, LoyaltyStatusDTO, PunctualityItemDTO, GrowthItemDTO
)

# Services
import services.analytics_service as analytics_services


analytics_router    = APIRouter()
version             = "/api/v1/"
collection          = "analytics"
endpoint            = f"{version}{collection}/"
tags                = "Analytics Services"

@analytics_router.get(
    path            = endpoint + "main-chart",
    response_model  = List[ MainChartItemDTO ],
    status_code     = status.HTTP_200_OK,
    tags            = [ tags ]
)
async def get_main_chart(
    year    : int,
    month   : Optional[ int ] = None,
    qr_type : Optional[ str ] = None
):
    return await analytics_services.get_main_chart( year, month, qr_type )


@analytics_router.get(
    path            = endpoint + "retention",
    response_model  = RetentionDTO,
    status_code     = status.HTTP_200_OK,
    tags            = [ tags ]
)
async def get_retention():
    return await analytics_services.get_retention()


@analytics_router.get(
    path            = endpoint + "loyalty",
    response_model  = List[ LoyaltyStatusDTO ],
    status_code     = status.HTTP_200_OK,
    tags            = [ tags ]
)
async def get_loyalty():
    return await analytics_services.get_loyalty_risk()


@analytics_router.get(
    path            = endpoint + "punctuality",
    response_model  = List[ PunctualityItemDTO ],
    status_code     = status.HTTP_200_OK,
    tags            = [ tags ]
)
async def get_punctuality():
    return await analytics_services.get_sunday_punctuality()


@analytics_router.get(
    path            = endpoint + "growth",
    response_model  = List[ GrowthItemDTO ],
    status_code     = status.HTTP_200_OK,
    tags            = [ tags ]
)
async def get_growth( year: int ):
    return await analytics_services.get_growth_by_month( year )
