from sqlalchemy import Column, Integer, String, ForeignKey
from ..database.db import Base

class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nama = Column(String(50), nullable=False)
    ras = Column(String(50))
    jenis_kelamin = Column(String(20))
    umur = Column(String(20))
    berat_badan = Column(String(20))