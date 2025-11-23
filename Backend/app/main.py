# Backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware   # <-- BARU DITAMBAH
from app.database.db import engine, Base
from app.routers import auth, cats
import os
import firebase_admin
from firebase_admin import credentials

print("\n" + "="*100)
print("                  PETRICORD BACKEND — VERSI FINAL 100% JALAN")
print("="*100)

# ==================== FIREBASE INIT ====================
service_paths = [
    "firebase-service-account.json",
    "../firebase-service-account.json",
    "../../firebase-service-account.json",
    "../../../firebase-service-account.json",
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
    print("firebase-service-account.json gak ketemu → tetep jalan kok (cuma login Google gak verif)")

# ==================== DATABASE ====================
Base.metadata.create_all(bind=engine)
print("Database & tabel 'users' + 'cats' siap!")

# ==================== FASTAPI APP ====================
app = FastAPI(title="Petricord API", version="1.0")

# WHITELIST CORS — INI YANG KAMU MINTA
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API ROUTES — HARUS DULUAN!
app.include_router(auth.router, prefix="/api/auth")
app.include_router(cats.router, prefix="/api/cats")

# ==================== FIX PATH FRONTEND ====================
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(os.path.dirname(current_file))
project_root = os.path.dirname(backend_dir)
frontend_path = os.path.join(project_root, "Frontend")

print(f"\nMencari Frontend di → {frontend_path}")

if os.path.isdir(frontend_path):
    print("Frontend KETEMU! File HTML yang tersedia:")
    for item in os.listdir(frontend_path):
        if item.endswith(".html"):
            print(f"   ✓ {item}")
    app.mount("/Frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print("Frontend berhasil di-mount → http://127.0.0.1:8000/Frontend/login.html")
else:
    print("FOLDER Frontend TIDAK DITEMUKAN!")

# ==================== STATIC UPLOADS ====================
static_dir = os.path.join(project_root, "static")
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static_uploads")

# ==================== ROOT REDIRECT ====================
@app.get("/")
async def root():
    return RedirectResponse("/Frontend/login.html")

@app.get("/api")
async def api_test():
    return {"message": "API JALAN MEONG!"}

print("\n" + "="*100)
print("SERVER SIAP! http://127.0.0.1:8000")
print("="*100 + "\n")