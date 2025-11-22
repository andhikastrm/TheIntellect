# app/dependencies.py

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

# INI YANG BENAR SESUAI STRUKTUR KAMU
from .database.db import get_db
from .models.user import User

# Firebase
import firebase_admin
from firebase_admin import auth as firebase_auth

# firebase_admin.initialize_app() harus dipanggil sekali di main.py
# (lihat langkah selanjutnya)

async def get_current_user_firebase(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ")[1].strip()

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
        name = decoded_token.get("name") or decoded_token.get("displayName") or "Petricord User"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cari user berdasarkan firebase_uid
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    # Kalau belum ada di DB, buat otomatis
    if not user:
        new_user = User(
            firebase_uid=firebase_uid,
            email=email or f"{firebase_uid}@petricord.local",
            nama=name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    return user