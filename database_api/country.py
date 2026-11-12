import re

from .db import get_db

def add_country(country_name: str, country_code: str):
    assert re.fullmatch(r"[A-Z]{3}", country_code)
    with get_db() as db:
        db.execute(
            "INSERT INTO Country (Country_Name, Country_Code) VALUES (%s, %s)",
            (country_name, country_code),
        )


def delete_country(country_name: str):
    with get_db() as db:
        db.execute("DELETE FROM Country WHERE Country_Name = %s", (country_name,))


def update_country(country_name: str, new_country_name: str):
    with get_db() as db:
        db.execute(
            "UPDATE Country SET Country_Name = %s WHERE Country_Name = %s",
            (new_country_name, country_name),
        )


def get_country(country_name: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Country WHERE Country_Name = %s", (country_name,)
        )
        return cur.fetchone()
