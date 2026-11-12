from .db import get_db


def add_race_distance(race_id: int, distance: str):
    with get_db() as db:
        db.execute(
            "INSERT INTO Race_Distances_Offered (Race_ID, Distance) VALUES (?, ?)",
            (race_id, distance),
        )


def delete_race_distance(race_id: int, distance: str):
    with get_db() as db:
        db.execute(
            """
            DELETE FROM Race_Distances_Offered
             WHERE Race_ID = ? AND Distance = ?
            """,
            (race_id, distance),
        )


def update_race_distance(race_id: int, distance: str, new_distance: str):
    with get_db() as db:
        db.execute(
            """
            UPDATE Race_Distances_Offered
               SET Distance = ?
             WHERE Race_ID = ? AND Distance = ?
            """,
            (new_distance, race_id, distance),
        )


def get_race_distance(race_id: int, distance: str):
    with get_db() as db:
        cur = db.execute(
            """
            SELECT * FROM Race_Distances_Offered
             WHERE Race_ID = ? AND Distance = ?
            """,
            (race_id, distance),
        )
        return cur.fetchone()


def get_race_distances(race_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Race_Distances_Offered WHERE Race_ID = ?", (race_id,)
        )
        return cur.fetchall()
