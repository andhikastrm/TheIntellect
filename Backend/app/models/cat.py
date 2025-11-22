# app/models/cat.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    ras = Column(String(100), nullable=True)
    usia = Column(String(50), nullable=True)
    berat_badan = Column(String(20), nullable=True)
    foto = Column(String(500), nullable=True)
    owner_email = Column(String(100), ForeignKey("users.email"))

    owner = relationship("User", back_populates="cats")