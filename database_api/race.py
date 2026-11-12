from datetime import date

from .db import get_db

_FACTORS = {40, 60, 80, 120, 160, 200, 240, 280}


def _as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(value)


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
    assert edition_number > 0
    assert factor in _FACTORS
    assert last_factor is None or last_factor in _FACTORS
    assert position is None or position > 0
    assert (tour_year is None) == (position is None)
    assert (championship_name is None) == (championship_year is None)

    race_day = _as_date(race_date)
    if previous_race_id is not None:
        assert previous_race_id != race_id
        row = db.execute(
            'SELECT Edition_Number, Race_Date FROM Race WHERE Race_ID = ?',
            (previous_race_id,),
        ).fetchone()
        if row is not None:
            previous_edition, previous_date = row
            assert previous_edition < edition_number
            assert _as_date(previous_date) < race_day


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
    with get_db() as db:
        _validate_race(
            db,
            None,
            previous_race_id,
            edition_number,
            race_date,
            factor,
            last_factor,
            tour_year,
            position,
            championship_name,
            championship_year,
        )
        cur = db.execute(
            """
            INSERT INTO Race
                (Race_Name, Race_Date, Edition_Number, Race_Link, Factor,
                 Last_Factor, Result_Link, Result_Link_Old, Category,
                 Additional_Info, Previous_Race_ID, Venue_Country, Venue_Name,
                 Tour_Year, Position, Championship_Name, Championship_Year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                race_name,
                race_date,
                edition_number,
                race_link,
                factor,
                last_factor,
                result_link,
                result_link_old,
                category,
                additional_info,
                previous_race_id,
                venue_country,
                venue_name,
                tour_year,
                position,
                championship_name,
                championship_year,
            ),
        )
        return cur.lastrowid


def delete_race(race_id: int):
    with get_db() as db:
        db.execute("DELETE FROM Race WHERE Race_ID = ?", (race_id,))


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
    with get_db() as db:
        _validate_race(
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
        )
        db.execute(
            """
            UPDATE Race
               SET Race_Name = ?, Race_Date = ?, Edition_Number = ?,
                   Race_Link = ?, Factor = ?, Last_Factor = ?, Result_Link = ?,
                   Result_Link_Old = ?, Category = ?, Additional_Info = ?,
                   Previous_Race_ID = ?, Venue_Country = ?, Venue_Name = ?,
                   Tour_Year = ?, Position = ?, Championship_Name = ?,
                   Championship_Year = ?
             WHERE Race_ID = ?
            """,
            (
                race_name,
                race_date,
                edition_number,
                race_link,
                factor,
                last_factor,
                result_link,
                result_link_old,
                category,
                additional_info,
                previous_race_id,
                venue_country,
                venue_name,
                tour_year,
                position,
                championship_name,
                championship_year,
                race_id,
            ),
        )


def get_race(race_id: int):
    with get_db() as db:
        cur = db.execute("SELECT * FROM Race WHERE Race_ID = ?", (race_id,))
        return cur.fetchone()
