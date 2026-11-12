from .db import get_db


def add_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        db.execute(
            "INSERT INTO Participates_In (Athlete_ID, Race_ID) VALUES (?, ?)",
            (athlete_id, race_id),
        )


def delete_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        db.execute(
            "DELETE FROM Participates_In WHERE Athlete_ID = ? AND Race_ID = ?",
            (athlete_id, race_id),
        )


def get_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Participates_In WHERE Athlete_ID = ? AND Race_ID = ?",
            (athlete_id, race_id),
        )
        return cur.fetchone()


def get_races_for_athlete(athlete_id: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Participates_In WHERE Athlete_ID = ?", (athlete_id,)
        )
        return cur.fetchall()


def get_athletes_for_race(race_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Participates_In WHERE Race_ID = ?", (race_id,)
        )
        return cur.fetchall()
