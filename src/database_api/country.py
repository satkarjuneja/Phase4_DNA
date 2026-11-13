import re

from .db import get_db
from .errors import check

_CODE = re.compile(r"^[A-Z]{3}$")


def add_country(country_name: str, country_code: str):
    check(country_name.strip(), "Country name is required")
    check(_CODE.match(country_code), "Country code must be exactly three capital letters (e.g. AUT)")
    with get_db() as db:
        db.execute(
            "INSERT INTO Country (Country_Name, Country_Code) VALUES (%s, %s)",
            (country_name, country_code),
        )


def delete_country(country_name: str):
    with get_db() as db:
        db.modify(
            "DELETE FROM Country WHERE Country_Name = %s",
            (country_name,),
            f"Country '{country_name}' not found",
        )


def update_country(country_name: str, country_code: str):
    check(_CODE.match(country_code), "Country code must be exactly three capital letters (e.g. AUT)")
    with get_db() as db:
        db.modify(
            "UPDATE Country SET Country_Code = %s WHERE Country_Name = %s",
            (country_code, country_name),
            f"Country '{country_name}' not found",
        )


def get_country(country_name: str):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Country WHERE Country_Name = %s",
            (country_name,),
            f"Country '{country_name}' not found",
        )


def list_countries():
    with get_db() as db:
        return db.fetch_all("SELECT Country_Name, Country_Code FROM Country ORDER BY Country_Name")
