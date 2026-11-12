from datetime import date

from .db import get_db


def _as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(value)


def _validate_race_result(db, race_id: int, place: int, points: float):
    assert place > 0
    assert points >= 0
    row = db.execute(
        "SELECT Race_Date FROM Race WHERE Race_ID = ?", (race_id,)
    ).fetchone()
    assert row is not None, f"Unknown race: {race_id}"
    assert _as_date(row[0]) <= date.today()


def add_race_result(
    athlete_id: str,
    race_id: int,
    place: int,
    finish_time: str,
    category: str,
    points: float = 0,
):
    with get_db() as db:
        _validate_race_result(db, race_id, place, points)
        db.execute(
            """
            INSERT INTO Race_Result
                (Athlete_ID, Race_ID, Place, Finish_Time, Category, Points)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (athlete_id, race_id, place, finish_time, category, points),
        )
        db.execute(
            """
            INSERT OR IGNORE INTO Participates_In (Athlete_ID, Race_ID)
            VALUES (?, ?)
            """,
            (athlete_id, race_id),
        )


def delete_race_result(athlete_id: str, race_id: int):
    with get_db() as db:
        db.execute(
            "DELETE FROM Race_Result WHERE Athlete_ID = ? AND Race_ID = ?",
            (athlete_id, race_id),
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
        _validate_race_result(db, race_id, place, points)
        db.execute(
            """
            UPDATE Race_Result
               SET Place = ?, Finish_Time = ?, Category = ?, Points = ?
             WHERE Athlete_ID = ? AND Race_ID = ?
            """,
            (place, finish_time, category, points, athlete_id, race_id),
        )


def get_race_result(athlete_id: str, race_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Race_Result WHERE Athlete_ID = ? AND Race_ID = ?",
            (athlete_id, race_id),
        )
        return cur.fetchone()
