from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..models.cat import Cat
from ..models.user import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/cats")
async def get_all_cats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")
    cats = db.query(Cat).all()
    result = []
    for cat in cats:
        owner = db.query(User).filter(User.id == cat.owner_id).first()
        result.append({**cat.__dict__, "owner_nama": owner.nama if owner else "Unknown"})
    return result