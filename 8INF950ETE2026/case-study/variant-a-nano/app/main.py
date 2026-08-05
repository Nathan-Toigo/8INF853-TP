from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import init_db
from app.routes.admin import router as admin_router
from app.routes.doctors import router as doctors_router
from app.routes.patients import router as patients_router
from app.routes.slots import router as slots_router
from app.routes.appointments import router as appointments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Gestion de rendez-vous médicaux",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(doctors_router, prefix="/doctors", tags=["doctors"])
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(slots_router, prefix="/doctors", tags=["slots"])
app.include_router(appointments_router, prefix="", tags=["appointments"])


@app.get("/health")
def health():
    return {"status": "ok"}