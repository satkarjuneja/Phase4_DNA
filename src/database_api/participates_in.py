from .db import get_db


def add_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        db.execute(
            "INSERT INTO Participates_In (Athlete_ID, Race_ID) VALUES (%s, %s)",
            (athlete_id, race_id),
        )


def delete_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Participates_In WHERE Athlete_ID = %s AND Race_ID = %s",
            (athlete_id, race_id),
            f"Athlete {athlete_id} is not registered for race {race_id}",
        )


def get_participates_in(athlete_id: str, race_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Participates_In WHERE Athlete_ID = %s AND Race_ID = %s",
            (athlete_id, race_id),
            f"Athlete {athlete_id} is not registered for race {race_id}",
        )


def get_races_for_athlete(athlete_id: str):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Participates_In WHERE Athlete_ID = %s", (athlete_id,)
        )


def get_athletes_for_race(race_id: int):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Participates_In WHERE Race_ID = %s", (race_id,)
        )
