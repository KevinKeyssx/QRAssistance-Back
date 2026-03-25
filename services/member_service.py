from typing             import List, Optional
from dtos.member_dto    import MemberUpdateDTO
from datetime           import datetime

# MongoDB
from beanie import init_beanie

# Database
from database import db

# Collections
from entities.member    import Member

async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ Member ]
	)


async def get_all_members() -> List[Member]:
    return await Member.find_all().to_list()


async def get_member_by_id(member_id: str) -> Optional[Member]:
    return await Member.get(member_id)


async def get_member_by_token(token: str) -> Optional[Member]:
    # Útil para cuando escaneen el QR físico
    return await Member.find_one(Member.ulid_token == token)


async def update_member(member_id: str, data: MemberUpdateDTO) -> Optional[Member]:
    member = await Member.get(member_id)

    if member:
        update_data = data.model_dump(exclude_unset=True)

        update_data["updated_at"] = datetime.utcnow()

        await member.set(update_data)

        return member
    return None


async def delete_member(member_id: str) -> bool:
    member = await Member.get(member_id)

    if member:
        await member.delete()

        return True
    return False