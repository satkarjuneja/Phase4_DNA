from .db import get_db
from .errors import check


def add_race_distance(race_id: int, distance: str):
    check(distance.strip(), "Distance is required")
    with get_db() as db:
        db.execute(
            "INSERT INTO Race_Distances_Offered (Race_ID, Distance) VALUES (%s, %s)",
            (race_id, distance),
        )


def delete_race_distance(race_id: int, distance: str):
    with get_db() as db:
        db.modify(
            "DELETE FROM Race_Distances_Offered WHERE Race_ID = %s AND Distance = %s",
            (race_id, distance),
            f"Distance '{distance}' not found for race {race_id}",
        )


def update_race_distance(race_id: int, distance: str, new_distance: str):
    check(new_distance.strip(), "New distance is required")
    with get_db() as db:
        db.modify(
            """
            UPDATE Race_Distances_Offered
               SET Distance = %s
             WHERE Race_ID = %s AND Distance = %s
            """,
            (new_distance, race_id, distance),
            f"Distance '{distance}' not found for race {race_id}",
        )


def get_race_distance(race_id: int, distance: str):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Race_Distances_Offered WHERE Race_ID = %s AND Distance = %s",
            (race_id, distance),
            f"Distance '{distance}' not found for race {race_id}",
        )


def get_race_distances(race_id: int):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Race_Distances_Offered WHERE Race_ID = %s", (race_id,)
        )
