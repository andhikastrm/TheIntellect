# backend/app/ml/detector.py
# VERSI FINAL — KHUSUS PETRICORD (BAHASA INDONESIA)

from ultralytics import YOLO
import cv2
import os
from datetime import datetime
from pathlib import Path

# ==================== PATH OTOMATIS ====================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "yolo_models" / "best.pt"
DETECTIONS_DIR = BASE_DIR / "static" / "detections"
UPLOADS_RAW_DIR = BASE_DIR / "static" / "uploads_raw"

# Buat folder kalau belum ada
DETECTIONS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Load model YOLOv8
try:
    model = YOLO(str(MODEL_PATH))
    print("Model YOLOv8 berhasil dimuat!")
except Exception as e:
    print(f"ERROR: Model tidak ditemukan di {MODEL_PATH}")
    print("   Taruh file 'yolov8_cat_behavior.pt' di folder 'backend/ml_models/'")
    raise e

# ==================== CLASS NAME SESUAI PERMINTAANMU (URUTAN HARUS SAMA DENGAN SAAT TRAINING!) ====================
CLASS_NAMES = [
    "buang air",    # 0
    "jalan",        # 1
    "kejang",       # 2
    "makan",        # 3
    "muntah",       # 4
    "tidur"         # 5
]

def detect_behavior(image_path: str):
    """
    Deteksi perilaku kucing dari gambar webcam
    Return: behavior (dalam bahasa Indonesia), confidence, dan gambar hasil deteksi
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Gambar tidak ditemukan: {image_path}")

    
    results = model(img, conf=0.35, iou=0.5)[0]  

    behavior = "tidak terdeteksi"
    confidence = 0.0

    if len(results.boxes) > 0:
        
        best_idx = results.boxes.conf.argmax()
        cls_id = int(results.boxes.cls[best_idx].item())
        confidence = float(results.boxes.conf[best_idx].item())

        if cls_id < len(CLASS_NAMES):
            behavior = CLASS_NAMES[cls_id]
        else:
            behavior = "tidak terdeteksi"

    
    annotated = results.plot(
        line_width=4,
        font_size=2,
        labels=True,
        conf=True,
        boxes=True
    )

    
    timestamp = int(datetime.now().timestamp())
    filename = f"detected_{timestamp}.jpg"
    save_path = DETECTIONS_DIR / filename
    cv2.imwrite(str(save_path), annotated)

    
    result_image_url = f"/static/detections/{filename}"

    return {
        "behavior": behavior,                    
        "confidence": round(confidence, 3),
        "image_result": result_image_url
    }