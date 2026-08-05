from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_seed_and_create_and_conflict():
    # Seed data
    r = client.post("/admin/seed")
    assert r.status_code in (200, 201)
    data = r.json()
    assert "message" in data

    # List doctors/patients
    doctors = client.get("/doctors").json()
    patients = client.get("/patients").json()
    assert len(doctors) >= 2
    assert len(patients) >= 2

    doctor_id = doctors[0]["id"]
    patient_id = patients[0]["id"]

    # Get slots for doctor 1
    slots = client.get(f"/doctors/{doctor_id}/slots").json()
    assert len(slots) >= 2

    slot0 = slots[0]
    start_at = datetime.fromisoformat(slot0["start_at"])
    # Create appointment within first slot
    payload = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "start_at": (start_at + timedelta(minutes=30)).isoformat(),
        "duration_minutes": 30,
        "reason": "Douleur temporaire (fictif)",
    }
    r1 = client.post("/appointments", json=payload)
    assert r1.status_code == 200, r1.text
    appt1 = r1.json()
    assert appt1["status"] == "SCHEDULED"

    # Try create overlapping appointment (conflict)
    payload2 = {
        "doctor_id": doctor_id,
        "patient_id": patients[1]["id"],
        "start_at": (start_at + timedelta(minutes=45)).isoformat(),  # overlaps with appt1
        "duration_minutes": 30,
        "reason": "Visite de contrôle (fictif)",
    }
    r2 = client.post("/appointments", json=payload2)
    assert r2.status_code == 409
    assert "Conflit" in r2.json()["detail"] or "chevauchement" in r2.json()["detail"]

def test_cancel():
    doctors = client.get("/doctors").json()
    patients = client.get("/patients").json()
    doctor_id = doctors[0]["id"]
    patient_id = patients[0]["id"]

    slots = client.get(f"/doctors/{doctor_id}/slots").json()
    slot0 = slots[1]
    start_at = datetime.fromisoformat(slot0["start_at"])

    payload = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "start_at": (start_at + timedelta(minutes=10)).isoformat(),
        "duration_minutes": 20,
        "reason": "Test annulation (fictif)",
    }
    r1 = client.post("/appointments", json=payload)
    assert r1.status_code == 200
    appt_id = r1.json()["id"]

    rc = client.post(f"/appointments/{appt_id}/cancel")
    assert rc.status_code == 200
    assert rc.json()["status"] == "CANCELED"