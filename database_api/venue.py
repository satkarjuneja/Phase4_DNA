from .db import get_db


def add_venue(
    country_name: str,
    name: str,
    number_of_stairs: int,
    city: str,
    special_info: str | None = None,
    street: str | None = None,
    postal_code: str | None = None,
):
    assert number_of_stairs > 0
    with get_db() as db:
        db.execute(
            """
            INSERT INTO Venue
                (Country_Name, Name, Number_of_Stairs, Special_Info, Street,
                 City, Postal_Code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                country_name,
                name,
                number_of_stairs,
                special_info,
                street,
                city,
                postal_code,
            ),
        )


def delete_venue(country_name: str, name: str):
    with get_db() as db:
        db.execute(
            "DELETE FROM Venue WHERE Country_Name = ? AND Name = ?",
            (country_name, name),
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
    assert number_of_stairs > 0
    with get_db() as db:
        db.execute(
            """
            UPDATE Venue
               SET Number_of_Stairs = ?, Special_Info = ?, Street = ?,
                   City = ?, Postal_Code = ?
             WHERE Country_Name = ? AND Name = ?
            """,
            (
                number_of_stairs,
                special_info,
                street,
                city,
                postal_code,
                country_name,
                name,
            ),
        )


def get_venue(country_name: str, name: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Venue WHERE Country_Name = ? AND Name = ?",
            (country_name, name),
        )
        return cur.fetchone()
