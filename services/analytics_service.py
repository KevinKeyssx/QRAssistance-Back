from datetime   import datetime
from typing     import List, Optional, Dict, Any

from entities.assistance    import Assistance
from dtos.analytics_dto     import (
    MainChartItemDTO, RetentionDTO, LoyaltyStatusDTO, PunctualityItemDTO, GrowthItemDTO
)

async def get_main_chart(
    year    : int,
    month   : Optional[ int ] = None,
    qr_type : Optional[ str ] = None
) -> List[ MainChartItemDTO ]:
    if month is not None:
        start_date  = datetime( year, month, 1 )

        if month == 12:
            end_date = datetime( year + 1, 1, 1 )
        else:
            end_date = datetime( year, month + 1, 1 )
    else:
        start_date  = datetime( year, 1, 1 )
        end_date    = datetime( year + 1, 1, 1 )

    match_cond : Dict[ str, Any ] = {
        "created_at": { "$gte": start_date, "$lt": end_date }
    }

    if qr_type:
        match_cond[ "qr.$id" ] = qr_type

    pipeline = [
        { "$match": match_cond },
        {
            "$lookup": {
                "from"          : "qrs",
                "localField"    : "qr.$id",
                "foreignField"  : "_id",
                "as"            : "qr_info"
            }
        },
        {
            "$unwind": {
                "path"                          : "$qr_info",
                "preserveNullAndEmptyArrays"    : True
            }
        },
        {
            "$group": {
                "_id": {
                    "label": { "$dayOfMonth": "$created_at" } if month else { "$month": "$created_at" },
                    "type" : "$qr_info.type"
                },
                "total": { "$sum": 1 }
            }
        },
        { "$sort": { "_id.label": 1 } }
    ]

    cursor  = await Assistance.get_motor_collection().aggregate( pipeline ).to_list( length=None )
    results = [ ]

    for doc in cursor:
        results.append( MainChartItemDTO(
            label   = doc[ "_id" ][ "label" ],
            type    = doc[ "_id" ].get( "type" ),
            total   = doc[ "total" ]
        ))

    return results


async def get_retention() -> RetentionDTO:
    pipeline = [
        {
            "$group": {
                "_id"               : "$member.$id",
                "total_assistances" : { "$sum": 1 },
                "first_time"        : { "$min": "$created_at" },
                "last_time"         : { "$max": "$created_at" }
            }
        },
        {
            "$project": {
                "is_recurring"          : { "$gt": [ "$total_assistances", 1 ] },
                "days_since_first_time" : {
                    "$dateDiff": { "startDate": "$first_time", "endDate": "$last_time", "unit": "day" }
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total_members": { "$sum": 1 },
                "recurring_members": { "$sum": { "$cond": [ "$is_recurring", 1, 0 ] } }
            }
        }
    ]

    cursor = await Assistance.get_motor_collection().aggregate( pipeline ).to_list( length=1 )

    if cursor:
        doc = cursor[ 0 ]
        return RetentionDTO(
            total_members       = doc[ "total_members" ],
            recurring_members   = doc[ "recurring_members" ]
        )

    return RetentionDTO( total_members=0, recurring_members=0 )


async def get_loyalty_risk() -> List[ LoyaltyStatusDTO ]:
    pipeline = [
        {
            "$group": {
                "_id"               : "$member.$id",
                "last_assistance"   : { "$max": "$created_at" }
            }
        },
        {
            "$addFields": {
                "days_absent": {
                    "$dateDiff": {
                        "startDate" : "$last_assistance",
                        "endDate"   : "$$NOW",
                        "unit"      : "day"
                    }
                }
            }
        },
        {
            "$project": {
                "status": {
                    "$switch": {
                        "branches": [
                            { "case": { "$lte": [ "$days_absent", 14 ] }, "then": "Active" },
                            { "case": { "$lte": [ "$days_absent", 28 ] }, "then": "At Risk" }
                        ],
                        "default": "Inactive/Drop-out"
                    }
                }
            }
        },
        {
            "$group": {
                "_id"           : "$status",
                "total_count"   : { "$sum": 1 },
                "members"       : { "$push": "$_id" }
            }
        }
    ]

    cursor  = await Assistance.get_motor_collection().aggregate( pipeline ).to_list( length=None )
    results = [ ]

    for doc in cursor:
        results.append( LoyaltyStatusDTO(
            status      = doc[ "_id" ],
            total_count = doc[ "total_count" ],
            members     = doc[ "members" ]
        ))

    return results


async def get_sunday_punctuality() -> List[ PunctualityItemDTO ]:
    pipeline = [
        {
            "$match": {
                "$expr": { "$eq": [ { "$dayOfWeek": "$created_at" }, 1 ] } 
            }
        },
        {
            "$project": {
                "hour": { "$hour": "$created_at" },
                "block": {
                    "$subtract": [
                        { "$minute": "$created_at" },
                        { "$mod": [ { "$minute": "$created_at" }, 15 ] }
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": { "hour": "$hour", "block": "$block" },
                "total": { "$sum": 1 }
            }
        },
        { "$sort": { "_id.hour": 1, "_id.block": 1 } }
    ]

    cursor  = await Assistance.get_motor_collection().aggregate( pipeline ).to_list( length=None )
    results = [ ]

    for doc in cursor:
        results.append( PunctualityItemDTO(
            hour    = doc[ "_id" ][ "hour" ],
            block   = doc[ "_id" ][ "block" ],
            total   = doc[ "total" ]
        ))

    return results


async def get_growth_by_month( year: int ) -> List[ GrowthItemDTO ]:
    # Growth comparing month vs month
    start_date  = datetime( year, 1, 1 )
    end_date    = datetime( year + 1, 1, 1 )

    # Optional: fetch previous year last month to calculate Jan growth
    start_prev  = datetime( year - 1, 12, 1 )

    pipeline = [
        {
            "$match": {
                "created_at": { "$gte": start_prev, "$lt": end_date }
            }
        },
        {
            "$group": {
                "_id": { "month": { "$month": "$created_at" }, "year": { "$year": "$created_at" } },
                "total": { "$sum": 1 }
            }
        },
        { "$sort": { "_id.year": 1, "_id.month": 1 } }
    ]

    cursor  = await Assistance.get_motor_collection().aggregate( pipeline ).to_list( length=None )

    data_dict = { }

    for doc in cursor:
        y = doc[ "_id" ][ "year" ]
        m = doc[ "_id" ][ "month" ]
        data_dict[ ( y, m ) ] = doc[ "total" ]

    results = [ ]

    for m in range( 1, 13 ):
        total_curr = data_dict.get( ( year, m ), 0 )

        # Determine previous month
        prev_m = m - 1
        prev_y = year

        if prev_m == 0:
            prev_m = 12
            prev_y = year - 1

        total_prev = data_dict.get( ( prev_y, prev_m ), 0 )

        growth = "N/A"

        if total_prev > 0:
            diff_pct = ( ( total_curr - total_prev ) / total_prev ) * 100
            growth = f"+{diff_pct:.1f}%" if diff_pct >= 0 else f"{diff_pct:.1f}%"
        elif total_curr > 0:
            growth = "+100.0%"

        results.append( GrowthItemDTO(
            year        = year,
            month       = m,
            total       = total_curr,
            growth      = growth
        ))

    return results
