# Backend/app/models/cat.py
# SEMUA MODEL (Cat + Device) DI SATU FILE → NO CIRCULAR IMPORT!

from sqlalchemy import Column, Integer, String, Enum, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum


# ===== ENUM =====
class JenisKelamin(enum.Enum):
    Jantan = "Jantan"
    Betina = "Betina"

class TipePerangkat(enum.Enum):
    GPS = "GPS"
    Kamera = "Kamera"
    Feeder = "Feeder"
    Lainnya = "Lainnya"

class StatusPerangkat(enum.Enum):
    Aktif = "Aktif"
    Nonaktif = "Nonaktif"
    #Rusak = "Rusak"


# ===== MODEL CAT =====
class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    umur = Column(Integer, nullable=True)
    jenis_kelamin = Column(Enum(JenisKelamin), nullable=False)
    ras = Column(String(100), nullable=True)
    warna = Column(String(50), nullable=True)
    berat_badan = Column(Float, nullable=True)
    foto = Column(String(500), nullable=True)
    deskripsi = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="cats")


# ===== MODEL DEVICE (SATU FILE DENGAN CAT) =====
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    nama_perangkat = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False)
    tipe = Column(Enum(TipePerangkat), nullable=False)
    status = Column(Enum(StatusPerangkat), default=StatusPerangkat.Aktif)
    assigned_at = Column(DateTime, default=datetime.utcnow)


class CatActivity(Base):
    __tablename__ = "cat_activities"

    id = Column(Integer, primary_key=True, index=True)
    behavior = Column(String(50), nullable=False)  
    confidence = Column(Float, nullable=False)
    image_path = Column(String(500))               
    detected_image = Column(String(500))           
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)