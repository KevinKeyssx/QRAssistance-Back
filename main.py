# FastApi
from fastapi                    import FastAPI
from fastapi.middleware.cors    import CORSMiddleware

# Routers
from routers.qr_router          import qr_router
from routers.member_router      import member_router
from routers.assistance_router  import assistance_router
from routers.survey_router      import survey_router
from routers.analytics_router   import analytics_router

# Services
from database import init_database

# New FastAPI
app = FastAPI(
	title       = 'QR Assistance',
	description = 'Asistencia por QR',
	version     = '0.0.1'
)

# !Only dev
# CORSMiddleware
origins = [ "*" ]

# middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins       = origins,
	allow_credentials   = True,
	allow_methods       = [ "*" ],
	allow_headers       = [ "*" ],
)

@app.on_event( "startup" )
async def start_database():
	await init_database()

# include_router
app.include_router( qr_router )
app.include_router( member_router )
app.include_router( assistance_router )
app.include_router( survey_router )
app.include_router( analytics_router )