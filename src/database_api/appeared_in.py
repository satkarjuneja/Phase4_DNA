from .db import get_db
from .errors import NotFoundError


def add_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        if not db.execute(
            "SELECT 1 FROM Race_Result WHERE Athlete_ID = %s AND Race_ID = %s",
            (athlete_id, race_id),
        ).fetchone():
            raise NotFoundError(f"Athlete {athlete_id} has no result for race {race_id}")
        db.execute(
            "INSERT INTO Appeared_In (Athlete_ID, Race_ID, Stat_ID) VALUES (%s, %s, %s)",
            (athlete_id, race_id, stat_id),
        )


def delete_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        db.modify(
            """
            DELETE FROM Appeared_In
             WHERE Athlete_ID = %s AND Race_ID = %s AND Stat_ID = %s
            """,
            (athlete_id, race_id, stat_id),
            "Appearance not found",
        )


def get_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        return db.fetch_one(
            """
            SELECT * FROM Appeared_In
             WHERE Athlete_ID = %s AND Race_ID = %s AND Stat_ID = %s
            """,
            (athlete_id, race_id, stat_id),
            "Appearance not found",
        )


def get_appearances_for_athlete(athlete_id: str):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Appeared_In WHERE Athlete_ID = %s", (athlete_id,)
        )


def get_appearances_for_stat(stat_id: int):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Appeared_In WHERE Stat_ID = %s", (stat_id,)
        )


def update_appeared_in(
    athlete_id: str, race_id: int, stat_id: int,
    new_athlete_id: str, new_race_id: int, new_stat_id: int,
):
    # One UPDATE, so the old row is never lost if the new values are invalid
    with get_db() as db:
        db.modify(
            """
            UPDATE Appeared_In
               SET Athlete_ID = %s, Race_ID = %s, Stat_ID = %s
             WHERE Athlete_ID = %s AND Race_ID = %s AND Stat_ID = %s
            """,
            (new_athlete_id, new_race_id, new_stat_id, athlete_id, race_id, stat_id),
            "Appearance not found",
        )
