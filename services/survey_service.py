# Python
from typing     import List, Optional
from datetime   import datetime

# Entities
from entities.surveys   import Survey
from entities.member    import Member
from entities.qr        import QR


async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ Survey ]
	)


async def get_survey_by_member_and_qr(
    member  : Member,
    qr      : QR
) -> Optional[ Survey ]:
    return await Survey.find_one(
        Survey.member.id == member.id,
        Survey.qr.id    == qr.id,
        fetch_links      = True
    )


async def get_all_surveys(
    year  : int,
    month : Optional[ int ] = None
) -> List[ Survey ]:
    if month:
        # Primer día del mes hasta primer día del mes siguiente
        next_year  = year + 1 if month == 12 else year
        next_month = 1        if month == 12 else month + 1

        start_range = datetime( year,      month,      1, 0, 0, 0 )
        end_range   = datetime( next_year, next_month, 1, 0, 0, 0 )
    else:
        # Año completo
        start_range = datetime( year, 1,  1,  0,  0,  0 )
        end_range   = datetime( year, 12, 31, 23, 59, 59 )

    return await (
        Survey
        .find(
            Survey.created_at >= start_range,
            Survey.created_at <  end_range,
            fetch_links       =  True
        )
        .sort( "-created_at" )
        .to_list()
    )


async def create_survey( survey: Survey ) -> Survey:
    created = await survey.insert()
    await created.fetch_all_links()
    return created


# async def update_survey(
#     survey_id   : str,
#     update_data : dict
# ) -> Optional[ Survey ]:
#     survey = await Survey.get( survey_id )

#     if not survey:
#         return None

#     update_data[ "updated_at" ] = datetime.utcnow()

#     await survey.set( update_data )

#     return survey


# async def delete_survey( survey_id: str ) -> bool:
#     survey = await Survey.get( survey_id )

#     if not survey:
#         return False

#     await survey.delete()

    # return True
