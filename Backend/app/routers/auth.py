from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from app.core.security import get_password_hash, create_access_token, verify_password
import os
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, validator

SERVICE_ACCOUNT_PATH = "secret/firebase-service-account.json"

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(f"Service account key tidak ditemukan: {SERVICE_ACCOUNT_PATH}")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

router = APIRouter()  

@router.post("/google-login")
async def firebase_login(request: Request, db: Session = Depends(get_db)):
    print("DEBUG: Login Google diterima")
    try:
        data = await request.json()
        token = data.get("token")
        if not token:
            raise HTTPException(400, "Token required")

        decoded = firebase_auth.verify_id_token(token)
        firebase_uid = decoded["uid"]
        email = decoded["email"]
        nama = decoded.get("name") or decoded.get("displayName") or email.split("@")[0]
        foto = decoded.get("picture")

        user = db.query(User).filter(
            (User.firebase_uid == firebase_uid) | (User.email == email)
        ).first()

        if user:
            if not user.firebase_uid:
                user.firebase_uid = firebase_uid
            if not user.foto_profil and foto:
                user.foto_profil = foto
            if not user.nama or user.nama == "Cordian":
                user.nama = nama
            db.commit()
            db.refresh(user)
        else:
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                nama=nama,
                foto_profil=foto,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token({"sub": str(user.id)})

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "nama": user.nama or "Cordian",
                "email": user.email,
                "foto_profil": user.foto_profil
            }
        }

    except Exception as e:
        print("ERROR AUTH:", e)
        raise HTTPException(500, "Login gagal")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    
    # Cari user berdasarkan email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )
    
    # Verifikasi password
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun ini menggunakan login Google"
        )
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )
    
    # Buat access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nama": user.nama or "Cordian",
            "email": user.email,
            "foto_profil": user.foto_profil,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "is_admin": user.is_admin
        }
    }

class RegisterRequest(BaseModel):
    nama: str | None = None
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    nama = (request.nama or "").strip() or email.split("@")[0]

    
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    
    hashed_pw = get_password_hash(request.password)

    
    new_user = User(
        email=email,
        nama=nama,
        hashed_password=hashed_pw,
        password=None,          
        role="user",            
        is_admin=False,
        firebase_uid=None,
        foto_profil=None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})

    return {
        "success": True,
        "message": "Akun berhasil dibuat!",
        "access_token": access_token,
        "user": {
            "id": new_user.id,
            "nama": nama,
            "email": email,
            "role": "user",
            "is_admin": False
        }
    }