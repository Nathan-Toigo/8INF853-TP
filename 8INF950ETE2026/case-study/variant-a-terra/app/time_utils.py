from datetime import datetime, timezone


def to_utc_naive(value: datetime) -> datetime:
    """
    Convertit une date timezone-aware en date UTC naïve.

    SQLite ne préserve pas systématiquement le fuseau horaire. L'application
    stocke donc les instants en UTC sans information de fuseau dans la base.
    """
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            "La date et l'heure doivent inclure un fuseau horaire, par exemple Z ou +01:00."
        )

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_iso(value: datetime) -> str:
    """Sérialise une date UTC naïve sous la forme ISO 8601 avec suffixe Z."""
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
