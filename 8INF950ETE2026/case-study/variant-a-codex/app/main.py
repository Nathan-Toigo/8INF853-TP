from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.routes import patients, doctors, appointments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion de rendez-vous médicaux", version="1.0.0")

app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])


@app.get("/health")
def health():
    return {"status": "ok"}
