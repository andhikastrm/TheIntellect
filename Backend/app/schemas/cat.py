from pydantic import BaseModel
from typing import Optional

class CatCreate(BaseModel):
    nama: str
    ras: Optional[str] = None
    usia: str
    berat_badan: float

    class Config:
        from_attributes = True


class CatResponse(BaseModel):
    id: int
    nama: str
    ras: Optional[str]
    usia: str
    berat_badan: float
    foto: Optional[str] = None
    user_firebase_uid: str

    class Config:
        from_attributes = True
