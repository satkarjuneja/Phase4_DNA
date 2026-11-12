from .db import get_db


def add_statistics(stat_rank: int, score: float, country_name: str):
    assert stat_rank > 0
    assert score >= 0
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO Statistics (Stat_Rank, Score, Country_Name) VALUES (%s, %s, %s)",
            (stat_rank, score, country_name),
        )
        return cur.lastrowid


def delete_statistics(stat_id: int):
    with get_db() as db:
        db.execute("DELETE FROM Statistics WHERE Stat_ID = %s", (stat_id,))


def update_statistics(stat_id: int, stat_rank: int, score: float, country_name: str):
    assert stat_rank > 0
    assert score >= 0
    with get_db() as db:
        db.execute(
            "UPDATE Statistics SET Stat_Rank = %s, Score = %s, Country_Name = %s WHERE Stat_ID = %s",
            (stat_rank, score, country_name, stat_id),
        )


def get_statistics(stat_id: int):
    with get_db() as db:
        cur = db.execute("SELECT * FROM Statistics WHERE Stat_ID = %s", (stat_id,))
        return cur.fetchone()
