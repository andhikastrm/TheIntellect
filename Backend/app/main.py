# Backend/app/main.py
# VERSI FIX — API JALAN + FRONTEND JALAN + UPLOAD FOTO JALAN

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.database.db import engine, Base
from app.routers import auth, cats
import os
import firebase_admin
from firebase_admin import credentials

print("\n" + "="*90)
print("                PETRICORD BACKEND — VERSI FIX 100% JALAN")
print("="*90)

# ==================== FIREBASE INIT ====================
service_paths = [
    "firebase-service-account.json",
    "../firebase-service-account.json",
    "../../firebase-service-account.json",
]

cred = None
for path in service_paths:
    full_path = os.path.abspath(path)
    if os.path.exists(full_path):
        cred = credentials.Certificate(full_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print(f"Firebase OK → {full_path}")
        break
if not cred:
    print("firebase-service-account.json gak ada → tapi tetep jalan")

# ==================== DATABASE ====================
Base.metadata.create_all(bind=engine)
print("Database & tabel siap!")

# ==================== FASTAPI APP ====================
app = FastAPI(title="Petricord API", version="1.0")

# ROUTE API DULUAN — INI YANG PENTING!!!
app.include_router(auth.router, prefix="/api/auth")
app.include_router(cats.router, prefix="/api/cats")  # WAJIB ADA PREFIX /api/cats

# ==================== MOUNT FRONTEND DI /Frontend (BUKAN DI / !!!) ====================
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_path = os.path.join(project_root, "Frontend")

if os.path.isdir(frontend_path):
    print(f"Frontend ditemukan → {frontend_path}")
    app.mount("/Frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print("Buka: http://127.0.0.1:8000/Frontend/add-cat.html")
else:
    print("Folder Frontend TIDAK ADA!")

# ==================== STATIC UPLOADS ====================
static_dir = os.path.join(project_root, "static")
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ==================== ROOT REDIRECT ====================
@app.get("/")
async def root():
    return RedirectResponse("/Frontend/login.html")

@app.get("/api")
async def api_test():
    return {"message": "API JALAN! /api/cats/ siap nerima POST"}

print("="*90)
print("SERVER JALAN! Buka → http://127.0.0.1:8000/Frontend/add-cat.html")
print("API aktif di → /api/cats/")
print("="*90 + "\n")