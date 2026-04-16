# MongoDB
import motor.motor_asyncio
from beanie import init_beanie

# Entities
from entities.qr            import QR
from entities.member        import Member
from entities.assistance    import Assistance
from entities.surveys       import Survey
from entities.whitelist     import WhiteList

# Env
import os
from dotenv import load_dotenv

load_dotenv( dotenv_path = '.env' )

db_name         = os.getenv( "MONGONAME" )
MONGOURL        = os.getenv( "MONGO_PUBLIC_URL" )
DATABASE_URL    = MONGOURL
client          = motor.motor_asyncio.AsyncIOMotorClient( DATABASE_URL )
db              = client[db_name]


async def init_database():
    """
    Inicializa la conexión de Beanie con todos los modelos de la aplicación.
    Se debe llamar una sola vez en el evento 'startup' de FastAPI.
    """
    await init_beanie(
        database=db,
        document_models=[
            QR,
            Member,
            Assistance,
            Survey,
            WhiteList
        ]
    )
