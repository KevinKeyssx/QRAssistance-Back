# MongoDB
from beanie     import init_beanie, Link
from database   import db

# Python
from typing import List, Optional, Tuple
from datetime   import datetime

# Entities
from entities.assistance    import Assistance
from entities.member        import Member
from entities.qr            import QR

# Dtos
from dtos.assistance_dto    import AssistanceCreateDTO
from dtos.paginated_dto     import Pagination


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
    query = Assistance.find( fetch_links=True )

    if member_query:
        # Buscamos miembros que coincidan con el nombre o apellido
        matching_members = await Member.find({
            "$or": [
                { "name"        : { "$regex": member_query, "$options": "i" } },
                { "last_name"   : { "$regex": member_query, "$options": "i" } }
            ]
        }).to_list()
        
        member_ids = [ m.id for m in matching_members ]
        query      = query.find({ "member.$id": { "$in": member_ids } })

    if qr_type:
        query = query.find({ "qr.type": qr_type })

    if date:
        start_of_day    = date.replace( hour=0, minute=0, second=0, microsecond=0 )
        end_of_day      = date.replace( hour=23, minute=59, second=59, microsecond=999999 )
        query           = query.find({"qr.date": { "$gte": start_of_day, "$lte": end_of_day }})

    total_count = await query.count()

    assistances = await query.skip(
        ( pagination.page - 1 ) * pagination.size
    ).limit( pagination.size ).to_list()

    result = [a for a in assistances if not isinstance( a.member, Link ) and not isinstance( a.qr, Link )]

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
