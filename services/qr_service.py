# Python
from typing     import List, Optional
from datetime   import datetime

# MongoDB
from beanie import init_beanie

# Database
from database import db

# Collections
from entities.qr import QR
from entities.assistance import Assistance


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


async def create_qrs( qrs_data: List[ QR ] ) -> List[ QR ]:
    if ( qrs_data ):
        await QR.insert_many( qrs_data )

    return qrs_data


async def get_qrs_by_date( target_date ) -> List[ QR ]:
    start_of_day    = datetime( target_date.year, target_date.month, target_date.day, 0, 0, 0 )
    end_of_day      = datetime( target_date.year, target_date.month, target_date.day, 23, 59, 59 )

    return await QR.find( QR.date >= start_of_day, QR.date <= end_of_day ).to_list()


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


async def get_all_qrs_with_stats(
    page: int = 1,
    size: int = 10,
    year: int = None
) -> dict:
    # 1. Obtener el rango del año actual
    current_year    = year or datetime.now().year
    start_of_year   = datetime( current_year, 1, 1, 0, 0, 0 )
    end_of_year     = datetime( current_year, 12, 31, 23, 59, 59 )

    # 2. Crear la consulta base con filtro de fecha
    query = QR.find( QR.date >= start_of_year, QR.date <= end_of_year )

    # 3. Calcular totales para la paginación
    total_items = await query.count()
    pages_count = ( total_items + size - 1 ) // size

    # 4. Obtener los QRs paginados
    qrs = await query.sort( "-date" ).skip(( page - 1 ) * size ).limit( size ).to_list()

    results = []

    for qr in qrs:
        count   = await Assistance.find( Assistance.qr.id == qr.id ).count()
        qr_dict = qr.model_dump()

        qr_dict["assist_count"] = count

        results.append( qr_dict )

    return {
        "items": results,
        "total": total_items,
        "page": page,
        "size": size,
        "pages": pages_count
    }
