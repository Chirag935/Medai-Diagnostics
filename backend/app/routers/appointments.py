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

class AppointmentRequestCreate(BaseModel):
    requested_date: str
    requested_time_frame: str # e.g. "Morning (09:00 - 12:00)"
    symptoms: str = ""

class AppointmentRequestApprove(BaseModel):
    doctor_id: int
    appointment_time: str
    notes: str = ""


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

# --- Appointment Requests Flow ---

@router.post("/request")
async def create_appointment_request(req: AppointmentRequestCreate, token: str):
    """Patient requests an appointment timeframe."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can request appointments")
        
    result = sb.table("appointment_requests").insert({
        "patient_id": user["id"],
        "requested_date": req.requested_date,
        "requested_time_frame": req.requested_time_frame,
        "symptoms": req.symptoms,
        "status": "pending"
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit request")
    return result.data[0]


@router.get("/requests")
async def list_appointment_requests(token: str):
    """Receptionists view all pending requests, Patients view their own."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] == "receptionist":
        result = sb.table("appointment_requests").select("*").order("created_at", desc=True).execute()
    elif user["role"] == "patient":
        result = sb.table("appointment_requests").select("*").eq("patient_id", user["id"]).order("created_at", desc=True).execute()
    else:
        return []
        
    requests = result.data or []
    
    # Enrich with patient names
    enriched = []
    for req in requests:
        patient_result = sb.table("users").select("name").eq("id", req.get("patient_id")).execute()
        patient_name = patient_result.data[0]["name"] if patient_result.data else "Unknown"
        enriched.append({**req, "patient_name": patient_name})
        
    return enriched


@router.get("/doctors-availability")
async def check_doctors_availability(date: str, token: str):
    """Receptionist checks which doctors are available on a specific date."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Only receptionists can check availability")
        
    # Get all doctors
    doctors_result = sb.table("users").select("id, name, specialization").eq("role", "doctor").execute()
    doctors = doctors_result.data or []
    
    # Get all appointments for that date
    appts_result = sb.table("appointments").select("doctor_id, appointment_time, status").eq("appointment_date", date).execute()
    appts = appts_result.data or []
    
    # Group appointments by doctor
    availability = []
    for doc in doctors:
        doc_appts = [a["appointment_time"] for a in appts if a["doctor_id"] == doc["id"] and a["status"] != "cancelled"]
        availability.append({
            "id": doc["id"],
            "name": doc["name"],
            "specialization": doc["specialization"],
            "booked_times": doc_appts
        })
        
    return availability


@router.post("/approve-request/{request_id}")
async def approve_appointment_request(request_id: int, approval: AppointmentRequestApprove, token: str):
    """Receptionist converts a pending request into a scheduled appointment."""
    sb = get_supabase()
    user = _get_user(sb, token)
    
    if user["role"] != "receptionist":
        raise HTTPException(status_code=403, detail="Only receptionists can approve requests")
        
    # Get the request
    req_result = sb.table("appointment_requests").select("*").eq("id", request_id).execute()
    if not req_result.data:
        raise HTTPException(status_code=404, detail="Request not found")
        
    request_data = req_result.data[0]
    
    if request_data["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request is already processed")
        
    # Create the official appointment
    appt_result = sb.table("appointments").insert({
        "patient_id": request_data["patient_id"],
        "doctor_id": approval.doctor_id,
        "receptionist_id": user["id"],
        "symptoms": request_data["symptoms"],
        "appointment_date": request_data["requested_date"],
        "appointment_time": approval.appointment_time,
        "notes": approval.notes,
        "status": "scheduled"
    }).execute()
    
    if not appt_result.data:
        raise HTTPException(status_code=500, detail="Failed to create appointment")
        
    # Update request status
    sb.table("appointment_requests").update({"status": "approved"}).eq("id", request_id).execute()
    
    return appt_result.data[0]
