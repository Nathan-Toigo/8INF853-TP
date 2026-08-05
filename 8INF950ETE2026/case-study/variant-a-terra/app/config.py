import os


class Settings:
    """Configuration centralisée de l'application."""

    app_name: str = "Gestion de rendez-vous médicaux"
    app_version: str = "1.0.0"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./medical_appointments.db",
    )


settings = Settings()
