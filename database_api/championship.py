from .db import get_db

_LEVELS = ("World", "Continental", "National")


def add_championship(name: str, year: int, level: str):
    assert 1000 <= year <= 9999
    assert level in _LEVELS
    with get_db() as db:
        db.execute(
            'INSERT INTO Championship (Name, "Year", "Level") VALUES (?, ?, ?)',
            (name, year, level),
        )


def delete_championship(name: str, year: int):
    with get_db() as db:
        db.execute(
            'DELETE FROM Championship WHERE Name = ? AND "Year" = ?',
            (name, year),
        )


def update_championship(name: str, year: int, level: str):
    assert level in _LEVELS
    with get_db() as db:
        db.execute(
            'UPDATE Championship SET "Level" = ? WHERE Name = ? AND "Year" = ?',
            (level, name, year),
        )


def get_championship(name: str, year: int):
    with get_db() as db:
        cur = db.execute(
            'SELECT * FROM Championship WHERE Name = ? AND "Year" = ?',
            (name, year),
        )
        return cur.fetchone()
