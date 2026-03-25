# FastApi
from fastapi                    import FastAPI
from fastapi.middleware.cors    import CORSMiddleware

# Routers
from routers.dynamicform import dynamicform

# Services
from services.form_service import init_db

# New FastAPI
app = FastAPI(
    title       = 'QR Assistance',
    description = 'Asistencia por QR',
    version     = '0.0.1'
)

# !Only dev
# CORSMiddleware
origins = ["*"]

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins       = origins,
    allow_credentials   = True,
    allow_methods       = ["*"],
    allow_headers       = ["*"],
)

@app.on_event("startup")
async def start_database():
    await init_db()

# include_router
app.include_router( dynamicform )