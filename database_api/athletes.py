import re
from datetime import date

from .db import get_db

_ATHLETE_ID = re.compile(r"^[A-Z]{3}[0-9]{4}[MF][0-9]{3}$")
_EMAIL = re.compile(r"^[^@ ]+@[^@ ]+[.][^@ ]+$")
_PHONE = re.compile(r"^\+[0-9]{7,15}$")
_GENDERS = ("Male", "Female")


def _as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(value)


def _validate_athlete(
    db, athlete_id: str, country_name: str, date_of_birth, gender: str
):
    assert _ATHLETE_ID.match(athlete_id)
    assert gender in _GENDERS

    dob = _as_date(date_of_birth)
    assert dob > date(1900, 1, 1)
    assert dob < date.today()

    row = db.execute(
        "SELECT Country_Code FROM Country WHERE Country_Name = ?", (country_name,)
    ).fetchone()
    assert row is not None, f"Unknown country: {country_name}"
    country_code = row[0]

    assert athlete_id[:3] == country_code
    assert athlete_id[3:7] == f"{dob.year:04d}"
    assert athlete_id[7] == ("M" if gender == "Male" else "F")


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
    assert _EMAIL.match(email_address)
    assert _PHONE.match(phone_number)
    with get_db() as db:
        assert (
            db.execute(
                "SELECT 1 FROM Team WHERE Member_ID = ?", (member_id,)
            ).fetchone()
            is None
        ), "Member is already a Team member"
        _validate_athlete(db, athlete_id, country_name, date_of_birth, gender)
        db.execute(
            """
            INSERT INTO Athletes
                (Athlete_ID, Member_ID, Email_Address, Phone_Number, Company_Name,
                 Date_of_Birth, Gender, Street, City, Postal_Code, Country_Name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                athlete_id,
                member_id,
                email_address,
                phone_number,
                company_name,
                date_of_birth,
                gender,
                street,
                city,
                postal_code,
                country_name,
            ),
        )


def delete_athlete(athlete_id: str):
    with get_db() as db:
        db.execute("DELETE FROM Athletes WHERE Athlete_ID = ?", (athlete_id,))


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
    assert _EMAIL.match(email_address)
    assert _PHONE.match(phone_number)
    with get_db() as db:
        _validate_athlete(db, athlete_id, country_name, date_of_birth, gender)
        db.execute(
            """
            UPDATE Athletes
               SET Member_ID = ?, Email_Address = ?, Phone_Number = ?,
                   Company_Name = ?, Date_of_Birth = ?, Gender = ?, Street = ?,
                   City = ?, Postal_Code = ?, Country_Name = ?
             WHERE Athlete_ID = ?
            """,
            (
                member_id,
                email_address,
                phone_number,
                company_name,
                date_of_birth,
                gender,
                street,
                city,
                postal_code,
                country_name,
                athlete_id,
            ),
        )


def get_athlete(athlete_id: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Athletes WHERE Athlete_ID = ?", (athlete_id,)
        )
        return cur.fetchone()
