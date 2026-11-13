import re
from datetime import date

from .db import get_db
from .errors import ValidationError, as_date, check

_TIME = re.compile(r"^\d{1,3}:[0-5]\d:[0-5]\d(\.\d{1,2})?$")


def _validate_race_result(db, race_id: int, place: int, finish_time: str, points: float):
    check(place > 0, "Place must be greater than 0")
    check(points >= 0, "Points cannot be negative")
    check(_TIME.match(finish_time), "Finish time must look like HH:MM:SS or HH:MM:SS.ss")
    row = db.fetch_one(
        "SELECT Race_Date FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found"
    )
    if as_date(row["Race_Date"]) > date.today():
        raise ValidationError("Results cannot be entered for a race in the future")


def add_race_result(
    athlete_id: str,
    race_id: int,
    place: int,
    finish_time: str,
    category: str,
    points: float = 0,
):
    with get_db() as db:
        _validate_race_result(db, race_id, place, finish_time, points)
        db.execute(
            """
            INSERT INTO Race_Result
                (Athlete_ID, Race_ID, Place, Finish_Time, Category, Points)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (athlete_id, race_id, place, finish_time, category, points),
        )
        db.execute(
            "INSERT IGNORE INTO Participates_In (Athlete_ID, Race_ID) VALUES (%s, %s)",
            (athlete_id, race_id),
        )


def delete_race_result(athlete_id: str, race_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Race_Result WHERE Athlete_ID = %s AND Race_ID = %s",
            (athlete_id, race_id),
            f"No result for athlete {athlete_id} in race {race_id}",
        )


def update_race_result(
    athlete_id: str,
    race_id: int,
    place: int,
    finish_time: str,
    category: str,
    points: float = 0,
):
    with get_db() as db:
        _validate_race_result(db, race_id, place, finish_time, points)
        db.modify(
            """
            UPDATE Race_Result
               SET Place = %s, Finish_Time = %s, Category = %s, Points = %s
             WHERE Athlete_ID = %s AND Race_ID = %s
            """,
            (place, finish_time, category, points, athlete_id, race_id),
            f"No result for athlete {athlete_id} in race {race_id}",
        )


def get_race_result(athlete_id: str, race_id: int):
    with get_db() as db:
        return db.fetch_one(
            """
            SELECT Athlete_ID, Race_ID, Place, CAST(Finish_Time AS CHAR) AS Finish_Time,
                   Category, Points
              FROM Race_Result
             WHERE Athlete_ID = %s AND Race_ID = %s
            """,
            (athlete_id, race_id),
            f"No result for athlete {athlete_id} in race {race_id}",
        )
