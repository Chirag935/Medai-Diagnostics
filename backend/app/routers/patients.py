from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import hashlib
import secrets
from datetime import datetime

router = APIRouter()

# --- Supabase Client ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(status_code=500, detail="Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in backend/.env")
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Models ---
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    specialization: str = "General Medicine"
    clinic_name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = ""

class ConsultationCreate(BaseModel):
    patient_id: int
    diagnosis: str
    symptoms: List[str] = []
    confidence: float = 0
    prescription: List[dict] = []
    notes: str = ""

# --- Auth Endpoints ---
@router.post("/register")
async def register(req: RegisterRequest):
    sb = get_supabase()
    
    # Check if email already exists
    existing = sb.table("doctors").select("id").eq("email", req.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    token = secrets.token_hex(32)
    result = sb.table("doctors").insert({
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "specialization": req.specialization,
        "clinic_name": req.clinic_name,
        "token": token,
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Registration failed")
    
    return {"token": token, "name": req.name, "email": req.email}

@router.post("/login")
async def login(req: LoginRequest):
    sb = get_supabase()
    
    result = sb.table("doctors").select("*").eq("email", req.email).eq("password_hash", hash_password(req.password)).execute()
    
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    doctor = result.data[0]
    token = secrets.token_hex(32)
    
    # Update token
    sb.table("doctors").update({"token": token}).eq("id", doctor["id"]).execute()
    
    return {
        "token": token,
        "doctor": {
            "id": doctor["id"],
            "name": doctor["name"],
            "email": doctor["email"],
            "specialization": doctor["specialization"],
            "clinic_name": doctor["clinic_name"],
        }
    }

@router.get("/me")
async def get_profile(token: str):
    sb = get_supabase()
    result = sb.table("doctors").select("*").eq("token", token).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid token")
    doctor = result.data[0]
    return {
        "id": doctor["id"],
        "name": doctor["name"],
        "email": doctor["email"],
        "specialization": doctor["specialization"],
        "clinic_name": doctor["clinic_name"],
    }

# --- Helper: get doctor from token ---
def _get_doctor_id(sb, token: str) -> int:
    result = sb.table("doctors").select("id").eq("token", token).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return result.data[0]["id"]

# --- Patient Endpoints ---
@router.post("/patients")
async def create_patient(patient: PatientCreate, token: str):
    sb = get_supabase()
    doctor_id = _get_doctor_id(sb, token)
    
    result = sb.table("patients").insert({
        "doctor_id": doctor_id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "blood_group": patient.blood_group,
        "allergies": patient.allergies or "",
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create patient")
    
    return {"id": result.data[0]["id"], "message": "Patient created successfully"}

@router.get("/patients")
async def list_patients(token: str):
    sb = get_supabase()
    doctor_id = _get_doctor_id(sb, token)
    
    result = sb.table("patients").select("*").eq("doctor_id", doctor_id).order("created_at", desc=True).execute()
    return result.data

@router.get("/patients/{patient_id}")
async def get_patient(patient_id: int, token: str):
    sb = get_supabase()
    doctor_id = _get_doctor_id(sb, token)
    
    patient = sb.table("patients").select("*").eq("id", patient_id).eq("doctor_id", doctor_id).execute()
    if not patient.data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    consultations = sb.table("consultations").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
    
    return {
        **patient.data[0],
        "consultations": consultations.data
    }

# --- Consultation Endpoints ---
@router.post("/consultations")
async def create_consultation(consult: ConsultationCreate, token: str):
    sb = get_supabase()
    doctor_id = _get_doctor_id(sb, token)
    
    result = sb.table("consultations").insert({
        "patient_id": consult.patient_id,
        "doctor_id": doctor_id,
        "diagnosis": consult.diagnosis,
        "symptoms": consult.symptoms,
        "confidence": consult.confidence,
        "prescription": consult.prescription,
        "notes": consult.notes,
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to record consultation")
    
    return {"id": result.data[0]["id"], "message": "Consultation recorded"}

@router.get("/stats")
async def get_stats(token: str):
    sb = get_supabase()
    doctor_id = _get_doctor_id(sb, token)
    
    patients = sb.table("patients").select("id", count="exact").eq("doctor_id", doctor_id).execute()
    consultations = sb.table("consultations").select("id", count="exact").eq("doctor_id", doctor_id).execute()
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_consults = sb.table("consultations").select("id", count="exact").eq("doctor_id", doctor_id).gte("created_at", f"{today}T00:00:00").execute()
    
    return {
        "total_patients": patients.count or 0,
        "total_consultations": consultations.count or 0,
        "today_consultations": today_consults.count or 0,
    }
