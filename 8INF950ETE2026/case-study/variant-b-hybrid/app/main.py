"""Point d'entrée de la variante B (hybride IA + revue humaine).

Contrairement à la variante A, chaque fonctionnalité ajoutée ici doit être
revue et testée avant d'être considérée comme terminée (voir README.md).
"""

from fastapi import FastAPI

app = FastAPI(title="Gestion de rendez-vous médicaux — Variante B (hybride)")


@app.get("/health")
def health() -> dict[str, str]:
    """Endpoint de santé utilisé par le monitoring et par les tests d'intégration CI."""
    return {"status": "ok"}
