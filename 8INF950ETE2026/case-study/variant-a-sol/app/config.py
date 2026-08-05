import os


class Settings:
    app_name: str = "Gestion de rendez-vous médicaux"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./medical_appointments.db",
    )
    default_appointment_duration_minutes: int = 30
    workday_start_hour: int = 8
    workday_end_hour: int = 18


settings = Settings()
