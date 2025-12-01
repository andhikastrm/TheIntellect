
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.requests import Request
from datetime import datetime
from app.models.cat import Device, CatActivity, Cat
from app.ml.detector import detect_behavior
from sqlalchemy.orm import Session  
from app.database.db import get_db
from app.models.user import User
from app.models.cat import Cat, Device
from typing import Optional, List
from app.core.security import get_current_user
from app.models.cat import MedicalRecord, CatActivityTodo
from datetime import datetime, date, timezone, timedelta
from sqlalchemy import func, and_
from ..schemas.cat import CatResponse, CatCreate, CatUpdate
import shutil
import os

WIB_OFFSET = timedelta(hours=7)
WIB_TZ = timezone(WIB_OFFSET, name="WIB")

router = APIRouter(tags=["Cats & Devices"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def time_ago(dt: datetime) -> str:
    if not dt:
        return "tidak diketahui"
    
    now = datetime.now(WIB_TZ)
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} hari lalu" if diff.days <= 7 else dt.strftime("%d %b %Y")
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    if hours > 0:
        return f"{hours} jam lalu"
    if minutes > 0:
        return f"{minutes} menit lalu"
    return "baru saja"



@router.post("/", status_code=status.HTTP_201_CREATED)
async def tambah_kucing(
    nama: str = Form(...),
    umur: int = Form(None),
    ras: str = Form(None),
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
        ras=ras,
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


@router.delete("/devicesdevices/{device_id}")
def hapus_perangkat(device_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(404, "Perangkat tidak ditemukan")
    db.delete(device)
    db.commit()
    return {"success": True}


@router.delete("/devices/serial/{serial_number}")
async def delete_device_by_serial(
    serial_number: str,
    db: Session = Depends(get_db)
):
    """
    Delete device by serial number
    """
    print(f"DEBUG: Attempting to delete device with serial: {serial_number}")
    
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        print(f"DEBUG: Device not found: {serial_number}")
        raise HTTPException(404, "Perangkat tidak ditemukan")
    
    print(f"DEBUG: Deleting device: {device.nama_perangkat} (ID: {device.id})")
    db.delete(device)
    db.commit()
    
    print(f"DEBUG: Device deleted successfully")
    return {
        "success": True,
        "message": "Perangkat berhasil dihapus"
    }



@router.put("/devices/{serial_number}")
async def update_device(
    serial_number: str,
    nama_perangkat: str = Form(...),
    user_email: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Update device name and assign user_id based on email
    """
    print(f"DEBUG: Updating device {serial_number}")
    print(f"DEBUG: New name: {nama_perangkat}")
    print(f"DEBUG: User email received: {user_email}")
    
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(404, "Perangkat tidak ditemukan")
    
    device.nama_perangkat = nama_perangkat
    
    if user_email:
        print(f"DEBUG: Looking for user with email: {user_email}")
        user = db.query(User).filter(User.email == user_email).first()
        print("user" , user)
        if user:
            print(f"DEBUG: User found! ID: {user.id}, Email: {user.email}")
            device.user_id = user.id
        else:
            print(f"DEBUG: WARNING - No user found with email: {user_email}")
    else:
        print("DEBUG: No user_email provided in request")
    
    db.commit()
    db.refresh(device)
    
    print(f"DEBUG: Device updated. user_id is now: {device.user_id}")
    
    return {
        "success": True,
        "message": "Perangkat berhasil diupdate",
        "device": {
            "id": device.id,
            "nama_perangkat": device.nama_perangkat,
            "serial_number": device.serial_number,
            "user_id": device.user_id
        }
    }




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

    
    new_device = Device(
        nama_perangkat=f"Smart Collar - {serial_number[-6:].upper()}",
        serial_number=serial_number,
        tipe="GPS",      
        status="Aktif"   
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

    
    device = db.query(Device).filter(Device.serial_number == serial_number).first()

    if not device:
        
        if not device:
            device = Device(
                nama_perangkat=f"Smart Collar - {serial_number}",
                serial_number=serial_number,
                tipe="Kamera",        
                status="Aktif"        
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            print(f"Device baru dibuat: {serial_number}")


    
    timestamp = int(datetime.now().timestamp())
    raw_filename = f"raw_{timestamp}.jpg"
    raw_path = f"static/uploads_raw/{raw_filename}"
    os.makedirs("static/uploads_raw", exist_ok=True)
    
    with open(raw_path, "wb") as f:
        f.write(await image.read())

    result = detect_behavior(raw_path)

    # Get user_id from device
    user_id = device.user_id if device else None
    print(f"DEBUG: Creating CatActivity with user_id: {user_id} from device: {serial_number}")
    
    # Simpan aktivitas dengan user_id
    activity = CatActivity(
        behavior=result["behavior"],
        confidence=result["confidence"],
        image_path=f"/static/uploads_raw/{raw_filename}",
        detected_image=result["image_result"],
        created_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    print(f"DEBUG: CatActivity created with ID: {activity.id}, user_id: {activity.user_id}")

    return {
        "success": True,
        "habit": result["behavior"],
        "confidence": result["confidence"],
        "image": result["image_result"],
        "timestamp": datetime.utcnow().isoformat(),
        "device_serial": serial_number,
        "user_id": user_id
    }


def time_ago(dt: datetime) -> str:
    if not dt:
        return "tidak diketahui"
    
    now = datetime.now(WIB_TZ)
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} hari lalu" if diff.days <= 7 else dt.strftime("%d %b %Y")
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    if hours > 0:
        return f"{hours} jam lalu"
    if minutes > 0:
        return f"{minutes} menit lalu"
    return "baru saja"

@router.get("/activities/latest-by-behavior")
async def get_latest_activity_per_behavior(db: Session = Depends(get_db)):
    try:
        
        subq = (
            db.query(
                CatActivity.behavior,
                func.max(CatActivity.id).label("max_id")  
            )
            .filter(CatActivity.behavior != "tidak terdeteksi")
            .group_by(CatActivity.behavior)
            .subquery()
        )

        
        activities = (
            db.query(CatActivity)
            .join(
                subq,
                and_(
                    CatActivity.behavior == subq.c.behavior,
                    CatActivity.id == subq.c.max_id
                )
            )
            .order_by(CatActivity.created_at.desc())
            .all()
        )

        result = []
        for act in activities:
            
            ts = act.created_at
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            ts_wib = ts.astimezone(WIB_TZ)

            result.append({
                "id": act.id,
                "behavior": act.behavior.capitalize(),
                "confidence": round(act.confidence * 100, 1),
                "timestamp": ts_wib.isoformat(),  
                "timestamp_display": ts_wib.strftime("%d %b %Y, %H:%M WIB"),
                "custom_name": "Kamera Utama",  
                "time_ago": time_ago(ts_wib)
            })

        return {"activities": result}

    except Exception as e:
        
        print(f"Error di latest-by-behavior: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data aktivitas terbaru")
    

@router.get("/activities/critical")
async def get_critical_activities(db: Session = Depends(get_db)):
    critical = db.query(CatActivity)\
        .filter(CatActivity.behavior.in_(["kejang", "muntah"]))\
        .order_by(CatActivity.created_at.desc())\
        .all()

    count_kejang = len([a for a in critical if a.behavior == "kejang"])
    count_muntah = len([a for a in critical if a.behavior == "muntah"])

    result = []
    for act in critical:
        device = db.query(Device).filter(Device.serial_number == getattr(act, 'device_serial', None)).first()
        custom_name = device.nama_perangkat if device else None

        result.append({
            "id": act.id,
            "behavior": act.behavior,
            "confidence": round(act.confidence * 100, 1),
            "timestamp": act.created_at.isoformat(),
            "device_serial": getattr(act, 'device_serial', 'Unknown'),
            "custom_name": custom_name or "Unknown Device"
        })

    return {
        "stats": {
            "kejang_count": count_kejang,
            "muntah_count": count_muntah,
            "total_critical": len(critical)
        },
        "activities": result
    }


# Helper function to save uploaded file
def save_upload_file(upload_file: UploadFile, destination: Path) -> str:
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(destination)
    finally:
        upload_file.file.close()


# GET all cats for current user
@router.get("/", response_model=dict)
async def get_my_cats(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    cats = db.query(Cat).filter(Cat.owner_id == user.id).all()
    
    if not cats:
        return {"kucings": []}
    
    return {
        "kucings": [
            {
                "id": cat.id,
                "nama": cat.nama,
                "ras": cat.ras,
                "umur": cat.umur,
                "berat_badan": cat.berat_badan,
                "foto": cat.foto,
                "deskripsi": cat.deskripsi,
            }
            for cat in cats
        ]
    }


# GET single cat by ID
@router.get("/{cat_id}", response_model=dict)
async def get_cat(
    cat_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    cat = db.query(Cat).filter(
        Cat.id == cat_id,
        Cat.owner_id == user.id
    ).first()
    
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    return {
        "kucing": {
            "id": cat.id,
            "nama": cat.nama,
            "ras": cat.ras,
            "umur": cat.umur,
            "berat_badan": cat.berat_badan,
            "foto": cat.foto,
            "deskripsi": cat.deskripsi,
        }
    }


# CREATE new cat
@router.post("/", response_model=dict)
async def create_cat(
    nama: str = Form(...),
    ras: Optional[str] = Form(None),
    umur: Optional[int] = Form(None),
    berat_badan: Optional[float] = Form(None),
    deskripsi: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Handle photo upload
    foto_path = None
    if foto:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/cats")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(foto.filename)[1]
        filename = f"cat_{user.id}_{int(os.time.time())}{file_extension}"
        file_path = upload_dir / filename
        
        # Save file
        foto_path = save_upload_file(foto, file_path)
    
    # Create new cat
    new_cat = Cat(
        nama=nama,
        ras=ras,
        umur=umur,
        berat_badan=berat_badan,
        foto=foto_path,
        deskripsi=deskripsi,
        owner_id=user.id
    )
    
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    
    return {
        "message": "Cat created successfully",
        "kucing": {
            "id": new_cat.id,
            "nama": new_cat.nama,
            "ras": new_cat.ras,
            "umur": new_cat.umur,
            "berat_badan": new_cat.berat_badan,
            "foto": new_cat.foto,
            "deskripsi": new_cat.deskripsi,
        }
    }


# UPDATE cat
@router.put("/{cat_id}", response_model=dict)
async def update_cat(
    cat_id: int,
    nama: Optional[str] = Form(None),
    ras: Optional[str] = Form(None),
    umur: Optional[int] = Form(None),
    berat_badan: Optional[float] = Form(None),
    deskripsi: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    cat = db.query(Cat).filter(
        Cat.id == cat_id,
        Cat.owner_id == user.id
    ).first()
    
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    # Update fields
    if nama is not None:
        cat.nama = nama
    if ras is not None:
        cat.ras = ras
    if umur is not None:
        cat.umur = umur
    if berat_badan is not None:
        cat.berat_badan = berat_badan
    if deskripsi is not None:
        cat.deskripsi = deskripsi
    
    # Handle photo upload
    if foto:
        # Delete old photo if exists
        if cat.foto and os.path.exists(cat.foto):
            try:
                os.remove(cat.foto)
            except:
                pass
        
        upload_dir = Path("uploads/cats")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = os.path.splitext(foto.filename)[1]
        filename = f"cat_{user.id}_{int(os.time.time())}{file_extension}"
        file_path = upload_dir / filename
        
        cat.foto = save_upload_file(foto, file_path)
    
    db.commit()
    db.refresh(cat)
    
    return {
        "message": "Cat updated successfully",
        "kucing": {
            "id": cat.id,
            "nama": cat.nama,
            "ras": cat.ras,
            "umur": cat.umur,
            "berat_badan": cat.berat_badan,
            "foto": cat.foto,
            "deskripsi": cat.deskripsi,
        }
    }


# DELETE cat
@router.delete("/{cat_id}", response_model=dict)
async def delete_cat(
    cat_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    cat = db.query(Cat).filter(
        Cat.id == cat_id,
        Cat.owner_id == user.id
    ).first()
    
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    # Delete photo file if exists
    if cat.foto and os.path.exists(cat.foto):
        try:
            os.remove(cat.foto)
        except:
            pass
    
    db.delete(cat)
    db.commit()
    
    return {
        "message": "Cat deleted successfully",
        "id": cat_id
    }


@router.get("/medical-records")
async def get_medical_records(cat_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    if cat_id:
        cat = db.query(Cat).filter(Cat.id == cat_id, Cat.owner_id == user.id).first()
        if not cat:
            raise HTTPException(404, "Kucing tidak ditemukan atau bukan milikmu")
    else:
        cat = db.query(Cat).filter(Cat.owner_id == user.id).first()
    if not cat:
        return {"records": []}

    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.cat_id == cat.id)
        .order_by(MedicalRecord.date.desc())
        .all()
    )
    
    return {
        "records": [
            {
                "id": r.id,
                "type": r.type,
                "date": r.date.isoformat(),
                "notes": r.notes or ""
            }
            for r in records
        ]
    }


@router.post("/medical-records")
async def create_medical_record(
    type: str = Form(...),
    date: date = Form(...),
    notes: str = Form(None),
    cat_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    
    if cat_id:
        cat = db.query(Cat).filter(Cat.id == cat_id, Cat.owner_id == user.id).first()
        if not cat:
            raise HTTPException(404, "Kucing tidak ditemukan atau bukan milikmu")
    else:
        cat = db.query(Cat).filter(Cat.owner_id == user.id).first()
    if not cat:
        raise HTTPException(404, "Kamu belum punya hewan")

    record = MedicalRecord(cat_id=cat.id, type=type, date=date, notes=notes)
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {"success": True, "record": {"id": record.id, "type": type, "date": str(date), "notes": notes or ""}}


@router.get("/todo-activities")
async def get_todo_activities(cat_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if cat_id:
        cat = db.query(Cat).filter(Cat.id == cat_id, Cat.owner_id == user.id).first()
        if not cat:
            raise HTTPException(404, "Kucing tidak ditemukan atau bukan milikmu")
    else:
        cat = db.query(Cat).filter(Cat.owner_id == user.id).first()
    if not cat:
        return {"activities": []}

    activities = (
        db.query(CatActivityTodo)
        .filter(CatActivityTodo.cat_id == cat.id)
        .filter(CatActivityTodo.is_done == False)
        .order_by(CatActivityTodo.date.asc().nulls_last(), CatActivityTodo.created_at.desc())
        .all()
    )
    
    return {
        "activities": [
            {
                "id": a.id,
                "text": a.text,
                "date": a.date.isoformat() if a.date else None
            }
            for a in activities
        ]
    }


@router.delete("/medical-records/{record_id}")
async def delete_medical_record(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "Rekaman medis tidak ditemukan")
    
    cat = db.query(Cat).filter(Cat.id == record.cat_id, Cat.owner_id == user.id).first()
    if not cat:
        raise HTTPException(403, "Bukan punyamu!")
    db.delete(record)
    db.commit()
    return {"success": True}


@router.post("/todo-activities")
async def create_todo_activity(
    text: str = Form(...),
    date: date = Form(None),
    cat_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if cat_id:
        cat = db.query(Cat).filter(Cat.id == cat_id, Cat.owner_id == user.id).first()
        if not cat:
            raise HTTPException(404, "Kucing tidak ditemukan atau bukan milikmu")
    else:
        cat = db.query(Cat).filter(Cat.owner_id == user.id).first()
    if not cat:
        raise HTTPException(404, "Kamu belum punya hewan")

    activity = CatActivityTodo(cat_id=cat.id, text=text, date=date)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return {"success": True, "activity": {"id": activity.id, "text": text, "date": str(date) if date else None}}


@router.delete("/todo-activities/{activity_id}")
async def complete_todo(activity_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    activity = db.query(CatActivityTodo).filter(CatActivityTodo.id == activity_id).first()
    if not activity:
        raise HTTPException(404, "Aktivitas tidak ditemukan")
    
    cat = db.query(Cat).filter(Cat.id == activity.cat_id, Cat.owner_id == user.id).first()
    if not cat:
        raise HTTPException(403, "Bukan punyamu!")

    activity.is_done = True
    db.commit()
    return {"success": True}