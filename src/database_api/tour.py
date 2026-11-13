from .db import get_db
from .errors import check


def add_tour(year: int, tour_name: str):
    check(1000 <= year <= 9999, "Tour year must be a four-digit year")
    with get_db() as db:
        db.execute(
            "INSERT INTO Tour (`Year`, Tour_Name) VALUES (%s, %s)",
            (year, tour_name),
        )


def delete_tour(year: int):
    with get_db() as db:
        db.modify("DELETE FROM Tour WHERE `Year` = %s", (year,), f"Tour {year} not found")


def update_tour(year: int, tour_name: str):
    with get_db() as db:
        db.modify(
            "UPDATE Tour SET Tour_Name = %s WHERE `Year` = %s",
            (tour_name, year),
            f"Tour {year} not found",
        )


def get_tour(year: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Tour WHERE `Year` = %s", (year,), f"Tour {year} not found"
        )
