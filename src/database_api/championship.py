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
