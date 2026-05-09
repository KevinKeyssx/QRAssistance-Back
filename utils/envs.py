# Python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv( dotenv_path = ".env" )

# Security
INTERNAL_SECRET_KEY = os.getenv( "INTERNAL_SECRET_KEY" )
GOOGLE_CLIENT_ID    = os.getenv( "GOOGLE_CLIENT_ID" )

# Configuration
TIMEZONE            = os.getenv( "TIMEZONE" )
ORIGINS             = os.getenv( "ORIGINS", "*" )
START_HOUR          = os.getenv( "START_HOUR" )
END_HOUR            = os.getenv( "END_HOUR" )

# Database
MONGONAME           = os.getenv( "MONGONAME" )
MONGO_PUBLIC_URL    = os.getenv( "MONGO_PUBLIC_URL" )

# Other
VISITING_MEMBER_ID  = os.getenv( "VISITING_MEMBER_ID" )
