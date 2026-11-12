from .db import get_db


def add_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        db.execute(
            "INSERT INTO Ranked_In (Athlete_ID, Ranking_ID) VALUES (?, ?)",
            (athlete_id, ranking_id),
        )


def delete_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        db.execute(
            "DELETE FROM Ranked_In WHERE Athlete_ID = ? AND Ranking_ID = ?",
            (athlete_id, ranking_id),
        )


def get_ranked_in(athlete_id: str, ranking_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Ranked_In WHERE Athlete_ID = ? AND Ranking_ID = ?",
            (athlete_id, ranking_id),
        )
        return cur.fetchone()


def get_rankings_for_athlete(athlete_id: str):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Ranked_In WHERE Athlete_ID = ?", (athlete_id,)
        )
        return cur.fetchall()


def get_athletes_for_ranking(ranking_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Ranked_In WHERE Ranking_ID = ?", (ranking_id,)
        )
        return cur.fetchall()
