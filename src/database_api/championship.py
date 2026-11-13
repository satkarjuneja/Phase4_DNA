from .db import get_db
from .errors import check

_LEVELS = ("World", "Continental", "National")


def add_championship(name: str, year: int, level: str):
    check(1000 <= year <= 9999, "Championship year must be a four-digit year")
    check(level in _LEVELS, f"Level must be one of: {', '.join(_LEVELS)}")
    with get_db() as db:
        db.execute(
            "INSERT INTO Championship (Name, `Year`, `Level`) VALUES (%s, %s, %s)",
            (name, year, level),
        )


def delete_championship(name: str, year: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Championship WHERE Name = %s AND `Year` = %s",
            (name, year),
            f"Championship '{name}' {year} not found",
        )


def update_championship(name: str, year: int, level: str):
    check(level in _LEVELS, f"Level must be one of: {', '.join(_LEVELS)}")
    with get_db() as db:
        db.modify(
            "UPDATE Championship SET `Level` = %s WHERE Name = %s AND `Year` = %s",
            (level, name, year),
            f"Championship '{name}' {year} not found",
        )


def get_championship(name: str, year: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Championship WHERE Name = %s AND `Year` = %s",
            (name, year),
            f"Championship '{name}' {year} not found",
        )


# ---------------------------------------------------------------------------
# Functional requirement: Statistics page -- championships by year with the
# race each one was held at. LEFT JOIN keeps championships whose race is not
# in the database.
# ---------------------------------------------------------------------------
def list_championships(level: str | None = None):
    check(level is None or level in _LEVELS, f"Level must be one of: {', '.join(_LEVELS)}")
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT ch.Name, ch.`Year`, ch.`Level`,
                   r.Race_ID, r.Race_Name, r.Race_Date, r.Venue_Name, r.Venue_Country
              FROM Championship ch
              LEFT JOIN Race r
                     ON r.Championship_Name = ch.Name AND r.Championship_Year = ch.`Year`
             WHERE (%s IS NULL OR ch.`Level` = %s)
             ORDER BY ch.`Year` DESC, FIELD(ch.`Level`, 'World', 'Continental', 'National'), ch.Name
            """,
            (level, level),
        )
