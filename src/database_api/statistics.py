from .db import get_db
from .errors import check


def _validate(stat_rank: int, score: float):
    check(stat_rank > 0, "Statistics rank must be greater than 0")
    check(score >= 0, "Statistics score cannot be negative")


def add_statistics(stat_rank: int, score: float, country_name: str):
    _validate(stat_rank, score)
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO Statistics (Stat_Rank, Score, Country_Name) VALUES (%s, %s, %s)",
            (stat_rank, score, country_name),
        )
        return cur.lastrowid


def delete_statistics(stat_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Statistics WHERE Stat_ID = %s",
            (stat_id,),
            f"Statistics entry {stat_id} not found",
        )


def update_statistics(stat_id: int, stat_rank: int, score: float, country_name: str):
    _validate(stat_rank, score)
    with get_db() as db:
        db.modify(
            "UPDATE Statistics SET Stat_Rank = %s, Score = %s, Country_Name = %s WHERE Stat_ID = %s",
            (stat_rank, score, country_name, stat_id),
            f"Statistics entry {stat_id} not found",
        )


def get_statistics(stat_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Statistics WHERE Stat_ID = %s",
            (stat_id,),
            f"Statistics entry {stat_id} not found",
        )
