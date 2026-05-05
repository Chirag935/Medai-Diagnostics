"""
Appointments Router — Receptionist schedules appointments between patients and doctors.
Doctors and patients can view their appointments.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
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
            raise HTTPException(status_code=500, detail="Supabase not configured")
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def _get_user(sb, token: str) -> dict:
    result = sb.table("users").select("*").eq("token", token).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return result.data[0]


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    symptoms: str = ""
    diagnosis_from_checker: str = ""
    appointment_date: str  # "2026-05-10"
    appointment_time: str  # "10:00"
    notes: str = ""


class AppointmentUpdate(BaseModel):
    status: str  # "scheduled", "completed", "cancelled"
    notes: Optional[str] = None


@router.post("/create")
async def create_appointment(appt: AppointmentCreate, token: str):
    """Receptionist creates an appointment."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Only receptionists can schedule appointments")
    
    result = sb.table("appointments").insert({
        "patient_id": appt.patient_id,
        "doctor_id": appt.doctor_id,
        "receptionist_id": user["id"],
        "symptoms": appt.symptoms,
        "diagnosis_from_checker": appt.diagnosis_from_checker,
        "appointment_date": appt.appointment_date,
        "appointment_time": appt.appointment_time,
        "notes": appt.notes,
        "status": "scheduled",
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create appointment")
    return result.data[0]


@router.get("/list")
async def list_appointments(token: str):
    """List appointments based on user role."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] == "receptionist":
        # Receptionists see all appointments they created
        result = sb.table("appointments").select("*").order("created_at", desc=True).execute()
    elif user["role"] == "doctor":
        # Doctors see appointments assigned to them
        result = sb.table("appointments").select("*").eq("doctor_id", user["id"]).order("created_at", desc=True).execute()
    elif user["role"] == "patient":
        # Patients see their own appointments
        result = sb.table("appointments").select("*").eq("patient_id", user["id"]).order("created_at", desc=True).execute()
    else:
        return []
    
    appointments = result.data or []
    
    # Enrich with user names
    enriched = []
    for appt in appointments:
        # Get patient name
        patient_result = sb.table("users").select("name").eq("id", appt.get("patient_id")).execute()
        patient_name = patient_result.data[0]["name"] if patient_result.data else "Unknown"
        
        # Get doctor name
        doctor_result = sb.table("users").select("name, specialization").eq("id", appt.get("doctor_id")).execute()
        doctor_name = doctor_result.data[0]["name"] if doctor_result.data else "Unknown"
        doctor_spec = doctor_result.data[0].get("specialization", "") if doctor_result.data else ""
        
        enriched.append({
            **appt,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "doctor_specialization": doctor_spec,
        })
    
    return enriched


@router.patch("/update/{appointment_id}")
async def update_appointment(appointment_id: int, update: AppointmentUpdate, token: str):
    """Update appointment status."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] not in ("receptionist", "doctor"):
        raise HTTPException(status_code=403, detail="Only receptionists and doctors can update appointments")
    
    update_data = {"status": update.status}
    if update.notes is not None:
        update_data["notes"] = update.notes
    
    result = sb.table("appointments").update(update_data).eq("id", appointment_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return result.data[0]


@router.get("/patients-list")
async def get_patients_for_scheduling(token: str):
    """Get list of patients (users with role=patient) for receptionist to schedule."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Only receptionists can access this")
    
    result = sb.table("users").select("id, name, email, phone").eq("role", "patient").execute()
    return result.data or []


@router.get("/doctors-list")
async def get_doctors_for_scheduling(token: str):
    """Get list of doctors for receptionist to assign."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Only receptionists can access this")
    
    result = sb.table("users").select("id, name, specialization, clinic_name").eq("role", "doctor").execute()
    return result.data or []
