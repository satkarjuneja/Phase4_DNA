from .db import get_db


def add_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        db.execute(
            "INSERT INTO Ranked_In (Athlete_ID, Ranking_ID) VALUES (%s, %s)",
            (athlete_id, ranking_id),
        )


def delete_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Ranked_In WHERE Athlete_ID = %s AND Ranking_ID = %s",
            (athlete_id, ranking_id),
            f"Athlete {athlete_id} is not linked to ranking {ranking_id}",
        )


def get_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Ranked_In WHERE Athlete_ID = %s AND Ranking_ID = %s",
            (athlete_id, ranking_id),
            f"Athlete {athlete_id} is not linked to ranking {ranking_id}",
        )


def get_rankings_for_athlete(athlete_id: str):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Ranked_In WHERE Athlete_ID = %s", (athlete_id,)
        )


def get_athletes_for_ranking(ranking_id: int):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Ranked_In WHERE Ranking_ID = %s", (ranking_id,)
        )


def update_ranked_in(athlete_id: str, ranking_id: int, new_athlete_id: str, new_ranking_id: int):
    # One UPDATE, so the old row is never lost if the new values are invalid
    with get_db() as db:
        db.modify(
            """
            UPDATE Ranked_In SET Athlete_ID = %s, Ranking_ID = %s
             WHERE Athlete_ID = %s AND Ranking_ID = %s
            """,
            (new_athlete_id, new_ranking_id, athlete_id, ranking_id),
            f"Athlete {athlete_id} is not linked to ranking {ranking_id}",
        )
