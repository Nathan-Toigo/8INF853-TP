import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_appointments.db")
