from .db import get_db
from .errors import check


def add_venue(
    country_name: str,
    name: str,
    number_of_stairs: int,
    city: str,
    special_info: str | None = None,
    street: str | None = None,
    postal_code: str | None = None,
):
    check(number_of_stairs > 0, "Number of stairs must be greater than 0")
    with get_db() as db:
        db.execute(
            """
            INSERT INTO Venue
                (Country_Name, Name, Number_of_Stairs, Special_Info, Street,
                 City, Postal_Code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (country_name, name, number_of_stairs, special_info, street, city, postal_code),
        )


def delete_venue(country_name: str, name: str):
    with get_db() as db:
        db.modify(
            "DELETE FROM Venue WHERE Country_Name = %s AND Name = %s",
            (country_name, name),
            f"Venue '{name}' in {country_name} not found",
        )


def update_venue(
    country_name: str,
    name: str,
    number_of_stairs: int,
    city: str,
    special_info: str | None = None,
    street: str | None = None,
    postal_code: str | None = None,
):
    check(number_of_stairs > 0, "Number of stairs must be greater than 0")
    with get_db() as db:
        db.modify(
            """
            UPDATE Venue
               SET Number_of_Stairs = %s, Special_Info = %s, Street = %s,
                   City = %s, Postal_Code = %s
             WHERE Country_Name = %s AND Name = %s
            """,
            (number_of_stairs, special_info, street, city, postal_code, country_name, name),
            f"Venue '{name}' in {country_name} not found",
        )


def get_venue(country_name: str, name: str):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Venue WHERE Country_Name = %s AND Name = %s",
            (country_name, name),
            f"Venue '{name}' in {country_name} not found",
        )
