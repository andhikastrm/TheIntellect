from sqlalchemy import Column, Integer, ForeignKey
from ..database.db import Base

class CatUser(Base):
    __tablename__ = "cat_user"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    cat_id = Column(Integer, ForeignKey("cats.id"), primary_key=True)