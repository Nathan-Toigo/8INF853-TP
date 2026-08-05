from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import appointments, patients, practitioners


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API de gestion de patients, praticiens et rendez-vous médicaux. "
        "Les dates et heures doivent être transmises avec un fuseau horaire "
        "et sont stockées en UTC."
    ),
    lifespan=lifespan,
)

app.include_router(patients.router)
app.include_router(practitioners.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Supervision"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
