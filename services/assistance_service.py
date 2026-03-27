from typing import List
from entities.assistance import Assistance
from entities.member import Member
from entities.qr import QR
from dtos.assistance_dto import AssistanceCreateDTO

# MongoDB
from beanie import init_beanie
from database import db


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


async def get_all_assistances() -> List[Assistance]:
    return await Assistance.find_all( fetch_links = True ).to_list()


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
