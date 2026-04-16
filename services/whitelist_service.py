from typing import List

# MongoDB
from beanie import init_beanie

# Database
from database import db

# Entities
from entities.whitelist import WhiteList


async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ WhiteList ]
	)


async def get_all_whitelist() -> List[WhiteList]:
    return await WhiteList.find_all().to_list()


async def have_permissions( email: str ) -> bool:
    return await WhiteList.find_one( WhiteList.email == email ) is not None


async def register_white_list( email: str ) -> WhiteList:
    new_entry = WhiteList( email = email )
    return await new_entry.insert()
