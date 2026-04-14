# Python
from typing         import List, Optional
from datetime       import datetime
from beanie         import Link
from collections    import defaultdict

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

    surveys = await (
        Survey
        .find(
            Survey.created_at >= start_range,
            Survey.created_at <  end_range,
            fetch_links       =  True
        )
        .sort( "-created_at" )
        .to_list()
    )

    return [ s for s in surveys if type(s.member) is not Link and type(s.qr) is not Link ]


async def create_survey( survey: Survey ) -> Survey:
    created = await survey.insert()
    await created.fetch_all_links()
    return created




async def get_survey_stats(
    year: int,
    month: Optional[int] = None,
    class_type: Optional[str] = None
):
    surveys = await get_all_surveys(year, month)

    stats = defaultdict(lambda: {"yes": 0, "no": 0})

    for s in surveys:
        if class_type and getattr(s.qr, 'type', None) != class_type:
            continue

        s_dict = s.model_dump() if hasattr(s, "model_dump") else s.dict()

        for field_name, answer in s_dict.items():
            if field_name.startswith("question"):
                stat_key = field_name.replace("question", "q")

                if answer:
                    stats[stat_key]["yes"] += 1
                else:
                    stats[stat_key]["no"] += 1

    return stats
