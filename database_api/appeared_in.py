from .db import get_db


def add_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        assert (
            db.execute(
                """
                SELECT 1 FROM Race_Result
                 WHERE Athlete_ID = %s AND Race_ID = %s
                """,
                (athlete_id, race_id),
            ).fetchone()
            is not None
        ), "Athlete has no result for this race"
        db.execute(
            """
            INSERT INTO Appeared_In (Athlete_ID, Race_ID, Stat_ID)
            VALUES (%s, %s, %s)
            """,
            (athlete_id, race_id, stat_id),
        )


def delete_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        db.execute(
            """
            DELETE FROM Appeared_In
             WHERE Athlete_ID = %s AND Race_ID = %s AND Stat_ID = %s
            """,
            (athlete_id, race_id, stat_id),
        )


def get_appeared_in(athlete_id: str, race_id: int, stat_id: int):
    with get_db() as db:
        cur = db.execute(
            """
            SELECT * FROM Appeared_In
             WHERE Athlete_ID = %s AND Race_ID = %s AND Stat_ID = %s
            """,
            (athlete_id, race_id, stat_id),
        )
        return cur.fetchone()


def get_appearances_for_athlete(athlete_id: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Appeared_In WHERE Athlete_ID = %s", (athlete_id,)
        )
        return cur.fetchall()


def get_appearances_for_stat(stat_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Appeared_In WHERE Stat_ID = %s", (stat_id,)
        )
        return cur.fetchall()
