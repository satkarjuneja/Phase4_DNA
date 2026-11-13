import re
from datetime import date

from .db import get_db
from .errors import ConflictError, NotFoundError, as_date, check, like_pattern

_ATHLETE_ID = re.compile(r"^[A-Z]{3}[0-9]{4}[MF][0-9]{3}$")
_EMAIL = re.compile(r"^[^@ ]+@[^@ ]+[.][^@ ]+$")
_PHONE = re.compile(r"^\+[0-9]{7,15}$")
_GENDERS = ("Male", "Female")


def _validate_athlete(
    db,
    athlete_id: str,
    email_address: str,
    phone_number: str,
    country_name: str,
    date_of_birth,
    gender: str,
):
    check(
        _ATHLETE_ID.match(athlete_id),
        "Athlete ID must look like POL1985M001 (country code, birth year, M/F, 3 digits)",
    )
    check(_EMAIL.match(email_address), "Email address is not valid")
    check(_PHONE.match(phone_number), "Phone number must start with + followed by 7 to 15 digits")
    check(gender in _GENDERS, "Gender must be 'Male' or 'Female'")

    dob = as_date(date_of_birth, "Date of birth")
    check(dob > date(1900, 1, 1), "Date of birth must be after 1900-01-01")
    check(dob < date.today(), "Date of birth must be in the past")

    row = db.execute(
        "SELECT Country_Code FROM Country WHERE Country_Name = %s", (country_name,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Country '{country_name}' not found")
    code = row["Country_Code"]

    check(athlete_id[:3] == code, f"Athlete ID must start with {code}, the code of {country_name}")
    check(athlete_id[3:7] == f"{dob.year:04d}", f"Athlete ID must contain the birth year {dob.year}")
    expected = "M" if gender == "Male" else "F"
    check(athlete_id[7] == expected, f"Athlete ID must have '{expected}' after the birth year for gender {gender}")


def add_athlete(
    athlete_id: str,
    member_id: int,
    email_address: str,
    phone_number: str,
    date_of_birth: str,
    gender: str,
    country_name: str,
    company_name: str | None = None,
    street: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
):
    with get_db() as db:
        if db.execute("SELECT 1 FROM Team WHERE Member_ID = %s", (member_id,)).fetchone():
            raise ConflictError(
                f"Member {member_id} is already a team member and cannot also be an athlete"
            )
        _validate_athlete(db, athlete_id, email_address, phone_number, country_name, date_of_birth, gender)
        db.execute(
            """
            INSERT INTO Athletes
                (Athlete_ID, Member_ID, Email_Address, Phone_Number, Company_Name,
                 Date_of_Birth, Gender, Street, City, Postal_Code, Country_Name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                athlete_id, member_id, email_address, phone_number, company_name,
                date_of_birth, gender, street, city, postal_code, country_name,
            ),
        )


def delete_athlete(athlete_id: str):
    with get_db() as db:
        db.modify(
            "DELETE FROM Athletes WHERE Athlete_ID = %s",
            (athlete_id,),
            f"Athlete {athlete_id} not found",
        )


def update_athlete(
    athlete_id: str,
    member_id: int,
    email_address: str,
    phone_number: str,
    date_of_birth: str,
    gender: str,
    country_name: str,
    company_name: str | None = None,
    street: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
):
    with get_db() as db:
        _validate_athlete(db, athlete_id, email_address, phone_number, country_name, date_of_birth, gender)
        db.modify(
            """
            UPDATE Athletes
               SET Member_ID = %s, Email_Address = %s, Phone_Number = %s,
                   Company_Name = %s, Date_of_Birth = %s, Gender = %s, Street = %s,
                   City = %s, Postal_Code = %s, Country_Name = %s
             WHERE Athlete_ID = %s
            """,
            (
                member_id, email_address, phone_number, company_name, date_of_birth,
                gender, street, city, postal_code, country_name, athlete_id,
            ),
            f"Athlete {athlete_id} not found",
        )


def get_athlete(athlete_id: str):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Athletes WHERE Athlete_ID = %s",
            (athlete_id,),
            f"Athlete {athlete_id} not found",
        )


# ---------------------------------------------------------------------------
# Functional requirement: athlete search (name or Athlete ID), with optional
# country/gender filters and a summary of each athlete's results.
# LEFT JOIN keeps athletes who have no results yet (0 races).
# ---------------------------------------------------------------------------
def search_athletes(
    search: str | None = None,
    country: str | None = None,
    gender: str | None = None,
):
    check(gender is None or gender in _GENDERS, "Gender must be 'Male' or 'Female'")
    pattern = like_pattern(search)
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT a.Athlete_ID,
                   m.First_Name, m.Last_Name,
                   a.Gender, a.Country_Name, c.Country_Code,
                   TIMESTAMPDIFF(YEAR, a.Date_of_Birth, CURDATE()) AS Age,
                   COUNT(rr.Race_ID)                             AS Races,
                   SUM(rr.Place = 1)                             AS Wins,
                   SUM(rr.Place <= 3)                            AS Podiums,
                   COALESCE(SUM(rr.Points), 0)                   AS Total_Points
              FROM Athletes a
              JOIN Members  m ON m.Member_ID    = a.Member_ID
              JOIN Country  c ON c.Country_Name = a.Country_Name
              LEFT JOIN Race_Result rr ON rr.Athlete_ID = a.Athlete_ID
             WHERE (%s IS NULL
                    OR CONCAT(m.First_Name, ' ', m.Last_Name) LIKE %s
                    OR a.Athlete_ID LIKE %s)
               AND (%s IS NULL OR a.Country_Name = %s)
               AND (%s IS NULL OR a.Gender = %s)
             GROUP BY a.Athlete_ID, m.First_Name, m.Last_Name, a.Gender,
                      a.Country_Name, c.Country_Code, a.Date_of_Birth
             ORDER BY Total_Points DESC, m.Last_Name, m.First_Name
            """,
            (pattern, pattern, pattern, country, country, gender, gender),
        )


# ---------------------------------------------------------------------------
# Functional requirement: athlete profile page -- personal data with the
# derived Age, every race result, and races registered for without a result.
# ---------------------------------------------------------------------------
def get_athlete_profile(athlete_id: str):
    with get_db() as db:
        profile = db.fetch_one(
            """
            SELECT a.Athlete_ID, m.Member_ID, m.First_Name, m.Last_Name,
                   a.Gender, a.Date_of_Birth,
                   TIMESTAMPDIFF(YEAR, a.Date_of_Birth, CURDATE()) AS Age,
                   a.Country_Name, c.Country_Code, a.Company_Name,
                   a.Email_Address, a.Phone_Number, a.Street, a.City, a.Postal_Code
              FROM Athletes a
              JOIN Members  m ON m.Member_ID    = a.Member_ID
              JOIN Country  c ON c.Country_Name = a.Country_Name
             WHERE a.Athlete_ID = %s
            """,
            (athlete_id,),
            f"Athlete {athlete_id} not found",
        )
        profile["results"] = db.fetch_all(
            """
            SELECT r.Race_ID, r.Race_Name, r.Race_Date, r.Factor,
                   r.Venue_Name, r.Venue_Country,
                   rr.Category, rr.Place,
                   CAST(rr.Finish_Time AS CHAR) AS Finish_Time, rr.Points
              FROM Race_Result rr
              JOIN Race r ON r.Race_ID = rr.Race_ID
             WHERE rr.Athlete_ID = %s
             ORDER BY r.Race_Date DESC
            """,
            (athlete_id,),
        )
        profile["registrations_without_result"] = db.fetch_all(
            """
            SELECT r.Race_ID, r.Race_Name, r.Race_Date, r.Venue_Name, r.Venue_Country,
                   (r.Race_Date >= CURDATE()) AS Upcoming
              FROM Participates_In pi
              JOIN Race r ON r.Race_ID = pi.Race_ID
              LEFT JOIN Race_Result rr
                     ON rr.Athlete_ID = pi.Athlete_ID AND rr.Race_ID = pi.Race_ID
             WHERE pi.Athlete_ID = %s
               AND rr.Race_ID IS NULL
             ORDER BY r.Race_Date DESC
            """,
            (athlete_id,),
        )
        return profile
