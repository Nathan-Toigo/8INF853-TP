from fastapi.testclient import TestClient


def create_patient(client: TestClient) -> int:
    response = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Martin",
            "birth_date": "1990-05-12",
            "phone": "+33612345678",
            "email": "alice.martin@example.test",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_practitioner(client: TestClient) -> int:
    response = client.post(
        "/practitioners",
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "specialty": "Médecine générale",
            "email": "jean.dupont@cabinet.test",
            "phone": "+33144556677",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_appointment(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-01-15T09:00:00",
            "end_at": "2030-01-15T09:30:00",
            "reason": "Consultation de suivi fictive",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["patient_id"] == patient_id
    assert payload["practitioner_id"] == practitioner_id
    assert payload["status"] == "scheduled"


def test_reject_overlapping_appointment(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    first_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-02-20T10:00:00",
            "end_at": "2030-02-20T10:30:00",
            "reason": "Contrôle fictif",
        },
    )
    assert first_response.status_code == 201

    conflict_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-02-20T10:15:00",
            "end_at": "2030-02-20T10:45:00",
            "reason": "Créneau conflictuel fictif",
        },
    )

    assert conflict_response.status_code == 409
    assert "créneau" in conflict_response.json()["detail"].lower()


def test_cancelled_appointment_frees_slot(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    appointment_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-03-10T14:00:00",
            "end_at": "2030-03-10T14:30:00",
            "reason": "Rendez-vous fictif à annuler",
        },
    )
    assert appointment_response.status_code == 201

    appointment_id = appointment_response.json()["id"]
    cancel_response = client.post(f"/appointments/{appointment_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    replacement_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-03-10T14:00:00",
            "end_at": "2030-03-10T14:30:00",
            "reason": "Nouveau rendez-vous fictif",
        },
    )

    assert replacement_response.status_code == 201
