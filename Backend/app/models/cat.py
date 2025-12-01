from sqlalchemy import Column, Integer, String, Enum, Float, Text, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum

class TipePerangkat(enum.Enum):
    GPS = "GPS"
    Kamera = "Kamera"
    Feeder = "Feeder"
    Lainnya = "Lainnya"

class StatusPerangkat(enum.Enum):
    Aktif = "Aktif"
    Nonaktif = "Nonaktif"


class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    umur = Column(Integer, nullable=True)
    berat_badan = Column(Float, nullable=True)
    foto = Column(String(500), nullable=True)
    ras = Column(String(100), nullable=True)
    deskripsi = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    medical_records = relationship("MedicalRecord", back_populates="cat", cascade="all, delete-orphan")
    todo_activities = relationship("CatActivityTodo", back_populates="cat", cascade="all, delete-orphan")

    owner = relationship("User", back_populates="cats")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    nama_perangkat = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False)
    tipe = Column(Enum(TipePerangkat), nullable=False)
    status = Column(Enum(StatusPerangkat), default=StatusPerangkat.Aktif)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    user = relationship("User", back_populates="devices")


class CatActivity(Base):
    __tablename__ = "cat_activities"

    id = Column(Integer, primary_key=True, index=True)
    behavior = Column(String(50), nullable=False)  
    confidence = Column(Float, nullable=False)
    image_path = Column(String(500))               
    detected_image = Column(String(500))           
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    user = relationship("User", back_populates="cat_activities")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)        # vaksin, grooming, checkup
    date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cat = relationship("Cat", back_populates="medical_records")


class CatActivityTodo(Base):
    __tablename__ = "cat_todo_activities"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)
    date = Column(Date, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cat = relationship("Cat", back_populates="todo_activities")