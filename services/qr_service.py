# Python
from typing     import List, Optional
from datetime   import datetime

# MongoDB
from beanie import init_beanie

# Database
from database import db

# Collections
from entities.qr import QR


async def init_db():
	await init_beanie(
		database        = db,
		document_models = [ QR ]
	)


async def get_qr_by_id( qr_id: str ) -> Optional[QR]:
    return await QR.get( qr_id )


async def get_all_qrs() -> List[ QR ]:
	qrs = await QR.find_all().to_list()

	return qrs


async def create_qr( qr_data: QR ) -> QR:
    return await qr_data.insert()


async def update_qr( qr_id: str, update_data: dict ) -> Optional[QR]:
    qr = await QR.get( qr_id )

    if qr:
        update_data["updated_at"] = datetime.utcnow()

        await qr.set( update_data )

        return qr

    return None


async def delete_qr( qr_id: str ) -> bool:
    qr = await QR.get( qr_id )

    if not qr:
        raise HTTPException(status_code=404, detail="QR no encontrado")

    await qr.delete()

    return True
