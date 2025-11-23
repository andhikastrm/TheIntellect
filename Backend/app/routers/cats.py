# app/routers/cats.py — VERSI FINAL 100% JALAN & BERSIH!

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from ..database.db import get_db
from ..models.cat import Cat
from ..models.cat_user import CatUser  # ← PASTIKAN ADA FILE models/cat_user.py
from ..models.user import User
from ..schemas.cat import CatCreate, CatResponse
from ..dependencies import get_current_user_firebase  # atau get_current_user

router = APIRouter(prefix="/api/cats", tags=["cats"])

# CREATE CAT
@router.post("/", response_model=CatResponse)
async def create_cat(
    nama: str = Form(...),
    ras: str = Form(None),
    usia: str = Form(...),
    berat_badan: float = Form(...),
    foto: UploadFile = File(None),
    current_user: User = Depends(get_current_user_firebase),
    db: Session = Depends(get_db)  # HANYA 1 DB!
):
    cat_data = {
        "nama": nama,
        "ras": ras or "Kampung",
        "usia": usia,
        "berat_badan": berat_badan
    }

    # Upload foto kalau ada
    if foto:
        foto_path = f"static/uploads/{foto.filename}"
        with open(foto_path, "wb") as f:
            content = await foto.read()
            f.write(content)
        cat_data["foto"] = f"/{foto_path}"

    # Simpan ke DB
    db_cat = Cat(**cat_data, user_firebase_uid=current_user.firebase_uid)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


# GET MY CATS
@router.get("/", response_model=List[CatResponse])  # List dari typing!
async def get_my_cats(
    current_user: User = Depends(get_current_user_firebase),
    db: Session = Depends(get_db)
):
    cats = db.query(Cat).filter(Cat.user_firebase_uid == current_user.firebase_uid).all()
    return cats