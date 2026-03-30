from typing             import List, Optional, Tuple
from dtos.member_dto    import MemberUpdateDTO
from datetime           import datetime

# DTOs
from dtos.paginated_dto import Pagination

# MongoDB
from beanie import init_beanie

# Database
from database import db

# Collections
from entities.member    import Member

# Utils
import unicodedata
import re


async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ Member ]
	)


async def get_all_members(
    pagination: Pagination
) -> List[Member]:
    return await Member.find_all(
        skip = ( pagination.page - 1 ) * pagination.size,
        limit = pagination.size
    ).to_list()


async def get_member_by_id( member_id: str ) -> Optional[Member]:
    return await Member.get( member_id )


async def get_member_by_token( token: str ) -> Optional[Member]:
    # Útil para cuando escaneen el QR físico
    return await Member.find_one( Member.ulid_token == token )


async def check_duplicate_member(
    name        : str,
    last_name   : str,
    classes     : List[ str ]
) -> bool:
    member = await Member.find_one(
        Member.name         == name,
        Member.last_name    == last_name,
        Member.classes      == classes
    )

    return member is not None


def build_accent_regex( query: str ) -> str:
    normalized = unicodedata.normalize( 'NFD', query ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
    safe_query = re.escape( normalized )

    mapping = {
        'a': '[aáàäâAÁÀÄÂ]', 'A': '[aáàäâAÁÀÄÂ]',
        'e': '[eéèëêEÉÈËÊ]', 'E': '[eéèëêEÉÈËÊ]',
        'i': '[iíìïîIÍÌÏÎ]', 'I': '[iíìïîIÍÌÏÎ]',
        'o': '[oóòöôOÓÒÖÔ]', 'O': '[oóòöôOÓÒÖÔ]',
        'u': '[uúùüûUÚÙÜÛ]', 'U': '[uúùüûUÚÙÜÛ]',
        'n': '[nñNÑ]',       'N': '[nñNÑ]',
        'c': '[cçCÇ]',       'C': '[cçCÇ]',
    }

    result = ""

    for char in safe_query:
        if char in mapping:
            result += mapping[ char ]
        else:
            result += char

    return f".*{result}.*"


async def get_members_by_name(
    query_text: str,
    pagination: Pagination
) -> Tuple[ List[ Member ], int ]:
    words               = query_text.strip().split()
    query_conditions    = []

    for word in words:
        regex_pattern = build_accent_regex( word )

        query_conditions.append({
            "$or": [
                { "name": { "$regex": regex_pattern, "$options": "i" } },
                { "last_name": { "$regex": regex_pattern, "$options": "i" } }
            ]
        })

    final_filter    = { "$and": query_conditions } if query_conditions else {}
    members         = await Member.find( final_filter ).skip( ( pagination.page - 1 ) * pagination.size ).limit( pagination.size ).to_list()
    total           = await Member.find( final_filter ).count()

    return members, total


async def update_member(
    member_id   : str,
    data        : MemberUpdateDTO
) -> Optional[Member]:
    member = await Member.get( member_id )

    if member:
        update_data = data.model_dump( exclude_unset=True )

        update_data["updated_at"] = datetime.utcnow()

        await member.set( update_data )

        return member
    return None


async def delete_member( member_id: str ) -> bool:
    member = await Member.get( member_id )

    if member:
        await member.delete()

        return True
    return False