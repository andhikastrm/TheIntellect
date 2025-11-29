# Backend/app/routers/cats.py — VERSI FINAL TERBAIK
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.requests import Request
from datetime import datetime
from app.models.cat import Device, CatActivity, Cat
from app.ml.detector import detect_behavior
from sqlalchemy.orm import Session  
from app.database.db import get_db
from app.models.user import User
from app.models.cat import Cat, Device
from app.core.security import get_current_user
import shutil
import os

router = APIRouter(tags=["Cats & Devices"])

UPLOAD_DIR = "static/uploads"
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

@router.get("/devices/public")
async def get_all_devices_public(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return [
        {
            "id": d.id,
            "nama_perangkat": d.nama_perangkat,
            "serial_number": d.serial_number,
            "tipe": d.tipe.value if hasattr(d.tipe, "value") else str(d.tipe),
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            # tambah field lain kalau perlu
        }
        for d in devices
    ]

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
def daftar_perangkat(db: Session = Depends(get_db), user=Depends(get_current_user)):
    devices = db.query(Device).all()
    return [d.__dict__ for d in devices]


@router.delete("/devices/{device_id}")
def hapus_perangkat(device_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(404, "Perangkat tidak ditemukan")
    db.delete(device)
    db.commit()
    return {"success": True}


# ==================== FITUR BARU: CEK / BUAT OTOMATIS BY SERIAL NUMBER ====================
@router.get("/devices/serial/{serial_number}")
def get_or_create_device_by_serial(
    serial_number: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    API ini akan:
    - Cek device berdasarkan serial_number
    - Kalau sudah ada → return detail
    - Kalau belum ada → BUAT BARU OTOMATIS lalu return detail
    """
    device = db.query(Device).filter(Device.serial_number == serial_number).first()

    if device:
        return {
            "exists": True,
            "message": "Device sudah terdaftar sebelumnya",
            "device": {
                "id": device.id,
                "nama_perangkat": device.nama_perangkat,
                "serial_number": device.serial_number,
                "tipe": device.tipe.value if hasattr(device.tipe, "value") else device.tipe,
                "status": device.status.value if hasattr(device.status, "value") else device.status,
                "cat_id": device.cat_id,
                "assigned_at": device.assigned_at.isoformat() if device.assigned_at else None
            }
        }

    # Belum ada → buat baru otomatis
    new_device = Device(
        nama_perangkat=f"Smart Collar - {serial_number[-6:].upper()}",
        serial_number=serial_number,
        tipe="GPS",      # default
        status="Aktif"   # default
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return {
        "exists": False,
        "message": "Device baru berhasil dibuat otomatis!",
        "device": {
            "id": new_device.id,
            "nama_perangkat": new_device.nama_perangkat,
            "serial_number": new_device.serial_number,
            "tipe": new_device.tipe.value if hasattr(new_device.tipe, "value") else new_device.tipe,
            "status": new_device.status.value if hasattr(new_device.status, "value") else new_device.status,
            "cat_id": None,
            "assigned_at": None
        }
    }
# ==================== API DETEKSI TANPA CAT_ID (PAKAI DEVICE SERIAL) ====================


@router.post("/detect-behavior")
async def detect_behavior_only(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    API DETEKSI KUCING — OTOMATIS BUAT DEVICE JIKA BELUM ADA
    Hanya butuh header: X-Device-Serial
    """
    serial_number = request.headers.get("X-Device-Serial")
    if not serial_number:
        raise HTTPException(status_code=400, detail="Header X-Device-Serial wajib dikirim")

    # CARI DEVICE — KALAU GAK ADA, BUAT BARU!
    device = db.query(Device).filter(Device.serial_number == serial_number).first()

    if not device:
        # BUAT DEVICE BARU OTOMATIS
        if not device:
            device = Device(
                nama_perangkat=f"Smart Collar - {serial_number}",
                serial_number=serial_number,
                tipe="Kamera",        # string → aman!
                status="Aktif"        # string → aman!
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            print(f"Device baru dibuat: {serial_number}")


    # LANJUT DETEKSI JIKA SUDAH ADA CAT_ID
    timestamp = int(datetime.now().timestamp())
    raw_filename = f"raw_{timestamp}.jpg"
    raw_path = f"static/uploads_raw/{raw_filename}"
    os.makedirs("static/uploads_raw", exist_ok=True)
    
    with open(raw_path, "wb") as f:
        f.write(await image.read())

    result = detect_behavior(raw_path)

    # Simpan aktivitas
    activity = CatActivity(
        behavior=result["behavior"],
        confidence=result["confidence"],
        image_path=f"/static/uploads_raw/{raw_filename}",
        detected_image=result["image_result"],
        created_at=datetime.utcnow()
    )
    db.add(activity)
    db.commit()

    return {
        "success": True,
        "habit": result["behavior"],
        "confidence": result["confidence"],
        "image": result["image_result"],
        "timestamp": datetime.utcnow().isoformat(),
        "device_serial": serial_number
    }