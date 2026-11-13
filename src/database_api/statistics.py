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


# ---------------------------------------------------------------------------
# Functional requirement: nations table -- every country that has athletes,
# ranked by the points its athletes earned, with a medal count. LEFT JOIN
# keeps countries whose athletes have no results yet (0 points).
# ---------------------------------------------------------------------------
def get_country_standings(gender: str | None = None):
    check(gender is None or gender in ("Male", "Female"), "Gender must be 'Male' or 'Female'")
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT RANK() OVER (ORDER BY COALESCE(SUM(rr.Points), 0) DESC) AS Position,
                   c.Country_Name, c.Country_Code,
                   COUNT(DISTINCT a.Athlete_ID)  AS Athletes,
                   COUNT(rr.Race_ID)             AS Results,
                   COALESCE(SUM(rr.Place = 1), 0) AS Gold,
                   COALESCE(SUM(rr.Place = 2), 0) AS Silver,
                   COALESCE(SUM(rr.Place = 3), 0) AS Bronze,
                   COALESCE(SUM(rr.Points), 0)    AS Total_Points
              FROM Country c
              JOIN Athletes a ON a.Country_Name = c.Country_Name
              LEFT JOIN Race_Result rr ON rr.Athlete_ID = a.Athlete_ID
             WHERE (%s IS NULL OR a.Gender = %s)
             GROUP BY c.Country_Name, c.Country_Code
             ORDER BY Position, c.Country_Name
            """,
            (gender, gender),
        )
