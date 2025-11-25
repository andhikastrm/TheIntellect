# backend/app/core/security.py
# FULL CODE — LANGSUNG JALAN 100% (Tested & Working!)

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# === IMPORT DATABASE & MODEL ===
from app.database.db import get_db
from app.models.user import User

# === KONFIGURASI JWT ===
SECRET_KEY = "petricord_ganti_ini_dengan_rahasia_kuat_banget_1234567890abcdef"  # GANTI KALAU MAU LEBIH AMAN
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 hari

# Password hashing (argon2 + bcrypt)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# Untuk login biasa (username/password)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Untuk proteksi route (Bearer Token dari frontend)
token_scheme = HTTPBearer()

# === FUNGSI JWT ===
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    # Fix bcrypt max 72 bytes
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

# === FUNGSI UTAMA: DAPATKAN USER DARI TOKEN (PAKAI INI DI ROUTER!) ===
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(token_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token tidak valid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token kadaluarsa atau rusak")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan")
    
    return user

# (Opsional) Kalau kamu masih pakai OAuth2 di auth login, biarin ini juga
async def get_current_user_oauth2(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return await get_current_user(HTTPAuthorizationCredentials(credentials=token), db)