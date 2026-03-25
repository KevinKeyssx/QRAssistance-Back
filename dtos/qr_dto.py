from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from entities.qr import QRType # Importamos el Enum que ya tienes

# 1. Para crear un QR (Lo que el cliente envía)
class QRCreateDTO(BaseModel):
    type: QRType
    date: datetime
    start_hour: str = Field(..., min_length=5, max_length=5, example="09:00")
    end_hour: str = Field(..., min_length=5, max_length=5, example="10:30")

# 2. Para actualizar un QR (Todo es opcional para permitir cambios parciales)
class QRUpdateDTO(BaseModel):
    type: Optional[QRType] = None
    date: Optional[datetime] = None
    start_hour: Optional[str] = Field(None, min_length=5, max_length=5)
    end_hour: Optional[str] = Field(None, min_length=5, max_length=5)

# 3. Para la respuesta (Lo que la API devuelve, incluyendo el ID)
class QRReadDTO(QRCreateDTO):
    id: str = Field(..., alias="_id") # Mapeamos el id de Beanie/Mongo
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True # Permite usar 'id' en el JSON aunque el alias sea '_id'