# Backend/app/models/cat.py
# SEMUA MODEL DALAM 1 FILE → AMAN, NO CIRCULAR IMPORT, SIAP PAKAI!

from sqlalchemy import Column, Integer, String, Enum, Float, Text, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum


# ===== ENUM =====

class TipePerangkat(enum.Enum):
    GPS = "GPS"
    Kamera = "Kamera"
    Feeder = "Feeder"
    Lainnya = "Lainnya"

class StatusPerangkat(enum.Enum):
    Aktif = "Aktif"
    Nonaktif = "Nonaktif"


# ===== MODEL CAT =====
class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    umur = Column(Integer, nullable=True)
    berat_badan = Column(Float, nullable=True)
    foto = Column(String(500), nullable=True)
    deskripsi = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # RELASI KE MEDICAL RECORD & TODO
    medical_records = relationship("MedicalRecord", back_populates="cat", cascade="all, delete-orphan")
    todo_activities = relationship("CatActivityTodo", back_populates="cat", cascade="all, delete-orphan")

    owner = relationship("User", back_populates="cats")


# ===== MODEL DEVICE =====
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    nama_perangkat = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False)
    tipe = Column(Enum(TipePerangkat), nullable=False)
    status = Column(Enum(StatusPerangkat), default=StatusPerangkat.Aktif)
    assigned_at = Column(DateTime, default=datetime.utcnow)


# ===== MODEL CAT ACTIVITY (DETEKSI ML) =====
class CatActivity(Base):
    __tablename__ = "cat_activities"

    id = Column(Integer, primary_key=True, index=True)
    behavior = Column(String(50), nullable=False)  
    confidence = Column(Float, nullable=False)
    image_path = Column(String(500))               
    detected_image = Column(String(500))           
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== MODEL MEDICAL RECORD (JURNAL HEWAN) =====
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)        # vaksin, grooming, checkup
    date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi balik ke Cat
    cat = relationship("Cat", back_populates="medical_records")


# ===== MODEL TODO ACTIVITY (TO-DO LIST / REMINDER) =====
class CatActivityTodo(Base):
    __tablename__ = "cat_todo_activities"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)
    date = Column(Date, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi balik ke Cat
    cat = relationship("Cat", back_populates="todo_activities")