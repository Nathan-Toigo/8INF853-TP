from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_end_to_end_flow():
    p = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Martin",
            "date_of_birth": "1990-04-10",
            "phone": "0600000001",
            "email": "alice.martin@example.test",
        },
    )
    assert p.status_code == 201
    patient_id = p.json()["id"]

    d = client.post(
        "/doctors",
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "specialty": "Cardiologie",
            "phone": "0600000101",
            "email": "jean.dupont@example.test",
        },
    )
    assert d.status_code == 201
    doctor_id = d.json()["id"]

    appt_time = (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0).isoformat()
    a = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "scheduled_at": appt_time,
            "duration_minutes": 30,
            "reason": "Contrôle annuel",
        },
    )
    assert a.status_code == 201
    appointment_id = a.json()["id"]

    overlap = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "scheduled_at": appt_time,
            "duration_minutes": 30,
            "reason": "Conflit attendu",
        },
    )
    assert overlap.status_code == 400

    c = client.patch(f"/appointments/{appointment_id}/cancel")
    assert c.status_code == 200
    assert c.json()["status"] == "cancelled"
