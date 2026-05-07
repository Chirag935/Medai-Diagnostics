import os
import random
import hashlib
from faker import Faker
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found in .env")
    exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
fake = Faker()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    print("Seeding 100 users...")
    users = []
    
    # 5 Receptionists
    for i in range(5):
        users.append({
            "name": fake.name(),
            "email": f"receptionist{i+1}@clinic.com",
            "password_hash": hash_password("password123"),
            "role": "receptionist",
            "clinic_name": "MedAI Central Clinic"
        })
        
    # 15 Doctors
    specializations = ['General Medicine', 'Dermatology', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics']
    docs_to_insert = []
    for i in range(15):
        doc = {
            "name": "Dr. " + fake.last_name(),
            "email": f"doctor{i+1}@clinic.com",
            "password_hash": hash_password("password123"),
            "role": "doctor",
            "specialization": random.choice(specializations),
            "clinic_name": "MedAI Central Clinic"
        }
        users.append(doc)
        docs_to_insert.append(doc)
        
    # 80 Patients
    pats_to_insert = []
    for i in range(80):
        pat = {
            "name": fake.name(),
            "email": f"patient{i+1}@gmail.com",
            "password_hash": hash_password("password123"),
            "role": "patient",
            "phone": fake.phone_number()
        }
        users.append(pat)
        pats_to_insert.append(pat)

    # Insert users
    for user in users:
        try:
            # Check if exists
            existing = sb.table("users").select("id").eq("email", user["email"]).execute()
            if not existing.data:
                sb.table("users").insert(user).execute()
        except Exception as e:
            print(f"Error inserting user {user['email']}: {e}")

    print("Users seeded successfully.")
    
    print("Seeding Patient Management System records...")
    # Fetch inserted doctors and patients to get their IDs
    docs_db = sb.table("users").select("id").eq("role", "doctor").execute().data
    pats_db = sb.table("users").select("*").eq("role", "patient").execute().data
    
    if docs_db and pats_db:
        for pat in pats_db:
            try:
                # Check if patient record exists
                existing = sb.table("patients").select("id").eq("name", pat["name"]).execute()
                if not existing.data:
                    # Randomly assign a doctor to the patient, or leave null if not required
                    sb.table("patients").insert({
                        "name": pat["name"],
                        "age": random.randint(18, 85),
                        "gender": random.choice(["Male", "Female", "Other"]),
                        "phone": pat.get("phone", fake.phone_number()),
                        "blood_group": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                        "allergies": random.choice(["None", "Peanuts", "Penicillin", "Dust", "Pollen"]),
                        "doctor_id": random.choice(docs_db)["id"]
                    }).execute()
            except Exception as e:
                pass
                
    print("Patient records seeded successfully.")

if __name__ == "__main__":
    seed_users()
    print("\n--- TEST CREDENTIALS ---")
    print("All passwords are: password123")
    print("Receptionist: receptionist1@clinic.com")
    print("Doctor: doctor1@clinic.com")
    print("Patient: patient1@gmail.com")
