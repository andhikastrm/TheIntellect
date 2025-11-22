# Backend/app/models/user.py
# VERSI FINAL — SUDAH ADA is_admin + IMPORT BOOLEAN + GAK ERROR LAGI!

from sqlalchemy import Column, Integer, String, DateTime, Boolean   # ← INI YANG WAJIB DITAMBAH
from sqlalchemy.orm import relationship
from app.database.db import Base  # pastikan ini bener
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Firebase UID (opsional kalau login Google)
    firebase_uid = Column(String(255), unique=True, index=True, nullable=True)
    
    # Email wajib ada
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Nama, foto, dll
    nama = Column(String(100), nullable=True)
    foto_profil = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # INI YANG BIKIN DIA BISA JADI ADMIN!
    is_admin = Column(Boolean, default=False, nullable=False)

    # Relasi ke kucing
    cats = relationship("Cat", back_populates="owner", cascade="all, delete-orphan")