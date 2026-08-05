from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_patient(client: TestClient) -> dict:
    response = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Martin",
            "email": "alice.martin@example.test",
            "phone": "+33102030405",
            "date_of_birth": "1988-04-12",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_practitioner(client: TestClient) -> dict:
    response = client.post(
        "/practitioners",
        json={
            "first_name": "Julien",
            "last_name": "Durand",
            "specialty": "Médecine générale",
            "email": "julien.durand@cabinet-example.test",
            "phone": "+33106070809",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_appointment_and_detect_conflict():
    with TestClient(app) as client:
        patient = create_patient(client)
        practitioner = create_practitioner(client)

        first_appointment = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-05-10T09:00:00Z",
                "ends_at": "2026-05-10T09:30:00Z",
                "reason": "Consultation de suivi fictive",
            },
        )

        assert first_appointment.status_code == 201
        assert first_appointment.json()["status"] == "scheduled"

        conflicting_appointment = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-05-10T09:15:00Z",
                "ends_at": "2026-05-10T09:45:00Z",
                "reason": "Créneau fictif en conflit",
            },
        )

        assert conflicting_appointment.status_code == 409
        assert "déjà un rendez-vous actif" in conflicting_appointment.json()["detail"]


def test_cancelled_appointment_releases_slot():
    with TestClient(app) as client:
        patient = create_patient(client)
        practitioner = create_practitioner(client)

        creation = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-06-15T14:00:00Z",
                "ends_at": "2026-06-15T14:30:00Z",
                "reason": "Consultation fictive à annuler",
            },
        )
        assert creation.status_code == 201

        appointment_id = creation.json()["id"]

        cancellation = client.post(
            f"/appointments/{appointment_id}/cancel",
            json={"cancellation_reason": "Patient fictif indisponible"},
        )
        assert cancellation.status_code == 200
        assert cancellation.json()["status"] == "cancelled"

        replacement = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-06-15T14:00:00Z",
                "ends_at": "2026-06-15T14:30:00Z",
                "reason": "Nouveau rendez-vous fictif",
            },
        )

        assert replacement.status_code == 201


def test_availability_endpoint():
    with TestClient(app) as client:
        practitioner = create_practitioner(client)

        response = client.get(
            "/appointments/availability",
            params={
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-07-01T10:00:00Z",
                "ends_at": "2026-07-01T10:30:00Z",
            },
        )

        assert response.status_code == 200
        assert response.json()["available"] is True
