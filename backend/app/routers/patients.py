from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import hashlib
import secrets
import json
from datetime import datetime

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "patients.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            specialization TEXT DEFAULT 'General Medicine',
            clinic_name TEXT DEFAULT '',
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            blood_group TEXT,
            allergies TEXT DEFAULT '',
            medical_history TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            symptoms TEXT DEFAULT '[]',
            confidence REAL DEFAULT 0,
            prescription TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Auth Models ---
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
    conn = get_db()
    try:
        token = secrets.token_hex(32)
        conn.execute(
            "INSERT INTO doctors (name, email, password_hash, specialization, clinic_name, token) VALUES (?, ?, ?, ?, ?, ?)",
            (req.name, req.email, hash_password(req.password), req.specialization, req.clinic_name, token)
        )
        conn.commit()
        return {"token": token, "name": req.name, "email": req.email}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()

@router.post("/login")
async def login(req: LoginRequest):
    conn = get_db()
    doctor = conn.execute(
        "SELECT * FROM doctors WHERE email = ? AND password_hash = ?",
        (req.email, hash_password(req.password))
    ).fetchone()
    conn.close()
    
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate new token
    token = secrets.token_hex(32)
    conn = get_db()
    conn.execute("UPDATE doctors SET token = ? WHERE id = ?", (token, doctor["id"]))
    conn.commit()
    conn.close()
    
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
    conn = get_db()
    doctor = conn.execute("SELECT * FROM doctors WHERE token = ?", (token,)).fetchone()
    conn.close()
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {
        "id": doctor["id"],
        "name": doctor["name"],
        "email": doctor["email"],
        "specialization": doctor["specialization"],
        "clinic_name": doctor["clinic_name"],
    }

# --- Patient Endpoints ---
@router.post("/patients")
async def create_patient(patient: PatientCreate, token: str):
    conn = get_db()
    doctor = conn.execute("SELECT id FROM doctors WHERE token = ?", (token,)).fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    
    cursor = conn.execute(
        "INSERT INTO patients (doctor_id, name, age, gender, phone, blood_group, allergies) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doctor["id"], patient.name, patient.age, patient.gender, patient.phone, patient.blood_group, patient.allergies)
    )
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return {"id": patient_id, "message": "Patient created successfully"}

@router.get("/patients")
async def list_patients(token: str):
    conn = get_db()
    doctor = conn.execute("SELECT id FROM doctors WHERE token = ?", (token,)).fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    
    patients = conn.execute(
        "SELECT * FROM patients WHERE doctor_id = ? ORDER BY created_at DESC", (doctor["id"],)
    ).fetchall()
    conn.close()
    
    return [dict(p) for p in patients]

@router.get("/patients/{patient_id}")
async def get_patient(patient_id: int, token: str):
    conn = get_db()
    doctor = conn.execute("SELECT id FROM doctors WHERE token = ?", (token,)).fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    
    patient = conn.execute(
        "SELECT * FROM patients WHERE id = ? AND doctor_id = ?", (patient_id, doctor["id"])
    ).fetchone()
    
    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    
    consultations = conn.execute(
        "SELECT * FROM consultations WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,)
    ).fetchall()
    conn.close()
    
    return {
        **dict(patient),
        "consultations": [dict(c) for c in consultations]
    }

# --- Consultation Endpoints ---
@router.post("/consultations")
async def create_consultation(consult: ConsultationCreate, token: str):
    conn = get_db()
    doctor = conn.execute("SELECT id FROM doctors WHERE token = ?", (token,)).fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    
    cursor = conn.execute(
        "INSERT INTO consultations (patient_id, doctor_id, diagnosis, symptoms, confidence, prescription, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (consult.patient_id, doctor["id"], consult.diagnosis, json.dumps(consult.symptoms),
         consult.confidence, json.dumps(consult.prescription), consult.notes)
    )
    conn.commit()
    consultation_id = cursor.lastrowid
    conn.close()
    return {"id": consultation_id, "message": "Consultation recorded"}

@router.get("/stats")
async def get_stats(token: str):
    conn = get_db()
    doctor = conn.execute("SELECT id FROM doctors WHERE token = ?", (token,)).fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")
    
    patient_count = conn.execute("SELECT COUNT(*) FROM patients WHERE doctor_id = ?", (doctor["id"],)).fetchone()[0]
    consultation_count = conn.execute("SELECT COUNT(*) FROM consultations WHERE doctor_id = ?", (doctor["id"],)).fetchone()[0]
    today_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE doctor_id = ? AND DATE(created_at) = DATE('now')", (doctor["id"],)
    ).fetchone()[0]
    conn.close()
    
    return {
        "total_patients": patient_count,
        "total_consultations": consultation_count,
        "today_consultations": today_count,
    }
