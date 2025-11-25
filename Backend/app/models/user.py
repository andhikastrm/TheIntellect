# Backend/app/models/user.py
# MODEL YANG BENAR-BENAR MATCH DENGAN TABEL users DI DATABASE KAMU (Nov 2025)

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, text
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum


# Kalau kamu pakai enum di MySQL, lebih aman pakai Python enum
class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    firebase_uid = Column(String(255), unique=True, index=True, nullable=True)

    email = Column(String(100), unique=True, index=True, nullable=False)

    # Kolom lama (yang masih ada di tabel kamu)
    password = Column(String(255), nullable=True)           # plain atau hash lama
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    # Kolom baru (yang kita pakai sekarang)
    hashed_password = Column(String(255), nullable=True)    # untuk bcrypt
    is_admin = Column(Boolean, default=False, nullable=False)

    nama = Column(String(100), nullable=True)
    foto_profil = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relasi ke kucing
    cats = relationship("Cat", back_populates="owner", cascade="all, delete-orphan")

    # Biar gampang ngecek role di code
    @property
    def is_admin_user(self) -> bool:
        return self.is_admin or self.role == UserRole.admin