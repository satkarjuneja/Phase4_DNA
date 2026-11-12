from .db import get_db


def add_tour(year: int, tour_name: str):
    assert 1000 <= year <= 9999
    with get_db() as db:
        db.execute(
            'INSERT INTO Tour ("Year", Tour_Name) VALUES (?, ?)',
            (year, tour_name),
        )


def delete_tour(year: int):
    with get_db() as db:
        db.execute('DELETE FROM Tour WHERE "Year" = ?', (year,))


def update_tour(year: int, tour_name: str):
    with get_db() as db:
        db.execute(
            'UPDATE Tour SET Tour_Name = ? WHERE "Year" = ?',
            (tour_name, year),
        )


def get_tour(year: int):
    with get_db() as db:
        cur = db.execute('SELECT * FROM Tour WHERE "Year" = ?', (year,))
        return cur.fetchone()
