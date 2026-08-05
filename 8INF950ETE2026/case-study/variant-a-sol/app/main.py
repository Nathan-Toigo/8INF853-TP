from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import appointments, patients, practitioners


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Gestion de rendez-vous médicaux",
    description=(
        "API REST de gestion des patients, praticiens et rendez-vous médicaux."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patients.router)
app.include_router(practitioners.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Système"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
