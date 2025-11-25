# Backend/app/routers/cats.py — VERSI FINAL TERBAIK
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.models.cat import Cat, Device
from app.core.security import get_current_user
import shutil
import os

router = APIRouter(prefix="/api/cats", tags=["Cats & Devices"])

UPLOAD_DIR = "TheIntellect/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==================== KUCING ====================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def tambah_kucing(
    nama: str = Form(...),
    umur: int = Form(None),
    jenis_kelamin: str = Form(...),
    ras: str = Form(None),
    warna: str = Form(None),
    berat_badan: float = Form(None),
    deskripsi: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    foto_path = None
    if foto and foto.filename:
        ext = os.path.splitext(foto.filename)[1]
        filename = f"cat_{current_user.id}_{int(__import__('time').time())}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(foto.file, f)
        foto_path = f"/static/uploads/{filename}"

    kucing = Cat(
        nama=nama,
        umur=umur,
        jenis_kelamin=jenis_kelamin,
        ras=ras,
        warna=warna,
        berat_badan=berat_badan,
        deskripsi=deskripsi,
        foto=foto_path,
        owner_id=current_user.id
    )
    db.add(kucing)
    db.commit()
    db.refresh(kucing)
    return {"success": True, "kucing": kucing.__dict__}


@router.get("/")
def daftar_kucing_saya(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kucings = db.query(Cat).filter(Cat.owner_id == user.id).all()
    return {"kucings": [k.__dict__ for k in kucings]}


@router.delete("/{cat_id}")
def hapus_kucing(cat_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kucing = db.query(Cat).filter(Cat.id == cat_id, Cat.owner_id == user.id).first()
    if not kucing:
        raise HTTPException(404, "Kucing tidak ditemukan")
    db.delete(kucing)
    db.commit()
    return {"success": True, "message": "Kucing dihapus"}


# ==================== PERANGKAT ====================
@router.post("/devices")
def tambah_perangkat(
    nama_perangkat: str = Form(...),
    serial_number: str = Form(...),
    tipe: str = Form(...),
    cat_id: int = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if db.query(Device).filter(Device.serial_number == serial_number).first():
        raise HTTPException(400, "Serial number sudah digunakan")

    device = Device(
        nama_perangkat=nama_perangkat,
        serial_number=serial_number,
        tipe=tipe,
        cat_id=cat_id
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"success": True, "device": device.__dict__}


@router.get("/devices")
def daftar_perangkat(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    devices = db.query(Device).all()
    return {"devices": [d.__dict__ for d in devices]}


@router.delete("/devices/{device_id}")
def hapus_perangkat(device_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(404, "Perangkat tidak ditemukan")
    db.delete(device)
    db.commit()
    return {"success": True}