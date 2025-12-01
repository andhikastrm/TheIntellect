from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, text
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    firebase_uid = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)        
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    hashed_password = Column(String(255), nullable=True)  
    is_admin = Column(Boolean, default=False, nullable=False)
    nama = Column(String(100), nullable=True)
    foto_profil = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False
    )
    cats = relationship("Cat", back_populates="owner", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    cat_activities = relationship("CatActivity", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin_user(self) -> bool:
        return self.is_admin or self.role == UserRole.admin