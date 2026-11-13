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


# ---------------------------------------------------------------------------
# Functional requirement: venue directory with how many races each venue has
# hosted and when the last/next one is. LEFT JOIN keeps venues with no races.
# ---------------------------------------------------------------------------
def list_venues(country: str | None = None, min_stairs: int | None = None):
    check(min_stairs is None or min_stairs >= 0, "Minimum stairs cannot be negative")
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT v.Country_Name, v.Name, v.City, v.Number_of_Stairs, v.Special_Info,
                   COUNT(r.Race_ID)                                         AS Races_Hosted,
                   MAX(CASE WHEN r.Race_Date <  CURDATE() THEN r.Race_Date END) AS Last_Race,
                   MIN(CASE WHEN r.Race_Date >= CURDATE() THEN r.Race_Date END) AS Next_Race
              FROM Venue v
              LEFT JOIN Race r
                     ON r.Venue_Country = v.Country_Name AND r.Venue_Name = v.Name
             WHERE (%s IS NULL OR v.Country_Name = %s)
               AND (%s IS NULL OR v.Number_of_Stairs >= %s)
             GROUP BY v.Country_Name, v.Name, v.City, v.Number_of_Stairs, v.Special_Info
             ORDER BY v.Number_of_Stairs DESC
            """,
            (country, country, min_stairs, min_stairs),
        )
