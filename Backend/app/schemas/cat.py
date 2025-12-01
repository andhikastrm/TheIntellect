from pydantic import BaseModel
from typing import Optional

class CatResponse(BaseModel):
    id: int
    nama: str
    ras: Optional[str] = None
    umur: Optional[int] = None
    berat_badan: Optional[float] = None
    foto: Optional[str] = None
    deskripsi: Optional[str] = None

    class Config:
        from_attributes = True


class CatCreate(BaseModel):
    nama: str
    ras: Optional[str] = None
    umur: Optional[int] = None
    berat_badan: Optional[float] = None
    deskripsi: Optional[str] = None


class CatUpdate(BaseModel):
    nama: Optional[str] = None
    ras: Optional[str] = None
    umur: Optional[int] = None
    berat_badan: Optional[float] = None
    deskripsi: Optional[str] = None
