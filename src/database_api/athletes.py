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
