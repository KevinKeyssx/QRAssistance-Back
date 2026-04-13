from pydantic   import BaseModel, Field
from typing     import List, Optional


class MainChartItemDTO( BaseModel ):
    label   : int = Field( ..., description="Day or Month" )
    type    : Optional[ str ] = Field( default=None, description="QR Type" )
    total   : int = Field( ..., description="Total assistances" )


class RetentionDTO( BaseModel ):
    total_members    : int = Field( alias="totalMembers" )
    recurring_members: int = Field( alias="recurringMembers" )

    class Config:
        populate_by_name = True


class LoyaltyStatusDTO( BaseModel ):
    status      : str           = Field( ..., description="Status (Active, At Risk, Inactive)" )
    total_count : int           = Field( alias="totalCount", description="Amount of members in this status" )
    members     : List[ str ]   = Field( description="List of members IDs" )

    class Config:
        populate_by_name = True


class PunctualityItemDTO( BaseModel ):
    hour    : int = Field( ..., description="Sunday hour" )
    block   : int = Field( ..., description="Minute block (0, 15, 30, 45)" )
    total   : int = Field( ..., description="Total assistances" )


class GrowthItemDTO( BaseModel ):
    year        : int               = Field( ..., description="Year" )
    month       : int               = Field( ..., description="Month" )
    total       : int               = Field( ..., description="Total assistances" )
    growth      : Optional[ str ]   = Field( default=None, description="Growth percentage compared to previous month" )
