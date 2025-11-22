# app/database/__init__.py
from .db import Base, engine, get_db   # TAMBAH get_db DI SINI !!!

__all__ = ["get_db", "engine", "Base", "SessionLocal"]