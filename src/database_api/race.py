import re
from datetime import date

from .db import get_db
from .errors import NotFoundError, as_date, check, like_pattern

_FACTORS = (40, 60, 80, 120, 160, 200, 240, 280)
_FACTOR_TEXT = ", ".join(map(str, _FACTORS))


def _validate_race(
    db,
    race_id,
    previous_race_id,
    edition_number,
    race_date,
    factor,
    last_factor,
    tour_year,
    position,
    championship_name,
    championship_year,
):
    check(edition_number > 0, "Edition number must be greater than 0")
    check(factor in _FACTORS, f"Factor must be one of {_FACTOR_TEXT}")
    check(last_factor is None or last_factor in _FACTORS, f"Last factor must be one of {_FACTOR_TEXT}")
    check(position is None or position > 0, "Tour position must be greater than 0")
    check((tour_year is None) == (position is None), "Tour year and position must both be set or both be empty")
    check(
        (championship_name is None) == (championship_year is None),
        "Championship name and year must both be set or both be empty",
    )

    race_day = as_date(race_date, "Race date")
    if previous_race_id is not None:
        check(previous_race_id != race_id, "A race cannot be its own previous edition")
        row = db.execute(
            "SELECT Edition_Number, Race_Date FROM Race WHERE Race_ID = %s",
            (previous_race_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"Previous edition race {previous_race_id} not found")
        check(
            row["Edition_Number"] < edition_number,
            f"Edition number must be greater than the previous edition's ({row['Edition_Number']})",
        )
        check(
            as_date(row["Race_Date"]) < race_day,
            f"Race date must be after the previous edition's date ({row['Race_Date']})",
        )


def add_race(
    race_name: str,
    race_date: str,
    edition_number: int,
    factor: int,
    venue_country: str,
    venue_name: str,
    race_link: str | None = None,
    last_factor: int | None = None,
    result_link: str | None = None,
    result_link_old: str | None = None,
    category: str | None = None,
    additional_info: str | None = None,
    previous_race_id: int | None = None,
    tour_year: int | None = None,
    position: int | None = None,
    championship_name: str | None = None,
    championship_year: int | None = None,
):
    check(race_name.strip(), "Race name is required")
    with get_db() as db:
        _validate_race(
            db, None, previous_race_id, edition_number, race_date, factor, last_factor,
            tour_year, position, championship_name, championship_year,
        )
        cur = db.execute(
            """
            INSERT INTO Race
                (Race_Name, Race_Date, Edition_Number, Race_Link, Factor,
                 Last_Factor, Result_Link, Result_Link_Old, Category,
                 Additional_Info, Previous_Race_ID, Venue_Country, Venue_Name,
                 Tour_Year, Position, Championship_Name, Championship_Year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                race_name, race_date, edition_number, race_link, factor, last_factor,
                result_link, result_link_old, category, additional_info, previous_race_id,
                venue_country, venue_name, tour_year, position, championship_name,
                championship_year,
            ),
        )
        return cur.lastrowid


def delete_race(race_id: int):
    with get_db() as db:
        db.modify("DELETE FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found")


def update_race(
    race_id: int,
    race_name: str,
    race_date: str,
    edition_number: int,
    factor: int,
    venue_country: str,
    venue_name: str,
    race_link: str | None = None,
    last_factor: int | None = None,
    result_link: str | None = None,
    result_link_old: str | None = None,
    category: str | None = None,
    additional_info: str | None = None,
    previous_race_id: int | None = None,
    tour_year: int | None = None,
    position: int | None = None,
    championship_name: str | None = None,
    championship_year: int | None = None,
):
    check(race_name.strip(), "Race name is required")
    with get_db() as db:
        _validate_race(
            db, race_id, previous_race_id, edition_number, race_date, factor, last_factor,
            tour_year, position, championship_name, championship_year,
        )
        db.modify(
            """
            UPDATE Race
               SET Race_Name = %s, Race_Date = %s, Edition_Number = %s,
                   Race_Link = %s, Factor = %s, Last_Factor = %s, Result_Link = %s,
                   Result_Link_Old = %s, Category = %s, Additional_Info = %s,
                   Previous_Race_ID = %s, Venue_Country = %s, Venue_Name = %s,
                   Tour_Year = %s, Position = %s, Championship_Name = %s,
                   Championship_Year = %s
             WHERE Race_ID = %s
            """,
            (
                race_name, race_date, edition_number, race_link, factor, last_factor,
                result_link, result_link_old, category, additional_info, previous_race_id,
                venue_country, venue_name, tour_year, position, championship_name,
                championship_year, race_id,
            ),
            f"Race {race_id} not found",
        )


def get_race(race_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found"
        )
