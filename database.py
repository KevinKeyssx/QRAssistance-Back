# MongoDB
import motor.motor_asyncio

# Env
import os
from dotenv import load_dotenv

load_dotenv( dotenv_path = '.env' )

db_name         = os.getenv( "MONGONAME" )
MONGOURL        = os.getenv( "MONGO_PUBLIC_URL" )
# MONGOURL        = os.getenv( "MONGO_LOCAL_URL" )
DATABASE_URL    = MONGOURL
client          = motor.motor_asyncio.AsyncIOMotorClient( DATABASE_URL )
db              = client[db_name]