from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_entities_and_appointment_flow():
    patient_payload = {
        "first_name": "Alice",
        "last_name": "Martin",
        "email": "alice.martin@example.test",
        "phone": "0600000001",
        "date_of_birth": "1992-05-10"
    }
    doctor_payload = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "specialty": "Cardiologie",
        "email": "jean.dupont@example.test",
        "phone": "0600000002"
    }

    p = client.post("/patients", json=patient_payload)
    d = client.post("/doctors", json=doctor_payload)
    assert p.status_code == 201, p.text
    assert d.status_code == 201, d.text

    patient_id = p.json()["id"]
    doctor_id = d.json()["id"]

    appt_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-01-10T10:00:00",
        "end_time": "2026-01-10T10:30:00",
        "reason": "Consultation de contrôle",
        "notes": "Douleurs thoraciques légères"
    }

    a = client.post("/appointments", json=appt_payload)
    assert a.status_code == 201, a.text

    conflict_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-01-10T10:15:00",
        "end_time": "2026-01-10T10:45:00",
        "reason": "Conflit",
        "notes": None
    }
    c = client.post("/appointments", json=conflict_payload)
    assert c.status_code == 409

    appt_id = a.json()["id"]
    upd = client.patch(f"/appointments/{appt_id}/status", json={"status": "completed"})
    assert upd.status_code == 200
    assert upd.json()["status"] == "completed"
