# FastAPI
from fastapi import Header, HTTPException, status

# Utils
from utils.envs import INTERNAL_SECRET_KEY

async def validate_internal_key( x_internal_key : str = Header( None, alias = "X-Internal-Key" ) ):
    """
    Dependencia para validar el header X-Internal-Key.
    Si la llave no viene o no coincide con la configurada en el servidor,
    se lanza una excepción 401.
    """
    if ( not INTERNAL_SECRET_KEY or x_internal_key != INTERNAL_SECRET_KEY ):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Servicio no autorizado"
        )
