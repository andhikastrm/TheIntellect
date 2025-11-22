from fastapi import Depends, HTTPException, Request
import firebase_admin
from firebase_admin import auth as firebase_auth

# Inisialisasi sekali
firebase_admin.initialize_app()

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Token required")
    
    token = auth_header.split("Bearer ")[1]
    try:
        decoded = firebase_auth.verify_id_token(token)
        request.state.user = decoded
        return decoded
    except:
        raise HTTPException(401, "Invalid token")