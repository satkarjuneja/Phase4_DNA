from .db import get_db
from .errors import check

_GENDERS = ("Male", "Female")


def _validate(ranking, score, gender, last_score, races, tour_points):
    check(ranking > 0, "Ranking position must be greater than 0")
    check(score >= 0, "Score cannot be negative")
    check(last_score is None or last_score >= 0, "Last score cannot be negative")
    check(races >= 0, "Races cannot be negative")
    check(tour_points >= 0, "Tour points cannot be negative")
    check(gender in _GENDERS, "Gender must be 'Male' or 'Female'")


def add_twa_ranking(
    country: str,
    ranking: int,
    score: float,
    gender: str,
    d_plus_minus: str | None = None,
    last_score: float | None = None,
    races: int = 0,
    tour_points: float = 0,
):
    _validate(ranking, score, gender, last_score, races, tour_points)
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO TWA_Ranking
                (Country, Ranking, D_Plus_Minus, Last_Score, Score, Races, Tour_Points, Gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (country, ranking, d_plus_minus, last_score, score, races, tour_points, gender),
        )
        return cur.lastrowid


def delete_twa_ranking(ranking_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM TWA_Ranking WHERE Ranking_ID = %s",
            (ranking_id,),
            f"Ranking entry {ranking_id} not found",
        )


def update_twa_ranking(
    ranking_id: int,
    country: str,
    ranking: int,
    score: float,
    gender: str,
    d_plus_minus: str | None = None,
    last_score: float | None = None,
    races: int = 0,
    tour_points: float = 0,
):
    _validate(ranking, score, gender, last_score, races, tour_points)
    with get_db() as db:
        db.modify(
            """
            UPDATE TWA_Ranking
               SET Country = %s, Ranking = %s, D_Plus_Minus = %s, Last_Score = %s,
                   Score = %s, Races = %s, Tour_Points = %s, Gender = %s
             WHERE Ranking_ID = %s
            """,
            (country, ranking, d_plus_minus, last_score, score, races, tour_points, gender, ranking_id),
            f"Ranking entry {ranking_id} not found",
        )


def get_twa_ranking(ranking_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM TWA_Ranking WHERE Ranking_ID = %s",
            (ranking_id,),
            f"Ranking entry {ranking_id} not found",
        )


# ---------------------------------------------------------------------------
# Functional requirement: TWA world ranking table (like the site's
# "TWA Ranking" page), one gender at a time, optionally for one country.
# ---------------------------------------------------------------------------
def get_ranking_table(gender: str, country: str | None = None, limit: int = 1000):
    check(gender in _GENDERS, "Gender must be 'Male' or 'Female'")
    check(1 <= limit <= 1000, "Limit must be between 1 and 1000")
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT t.Ranking_ID, t.Ranking, t.D_Plus_Minus,
                   a.Athlete_ID, CONCAT(m.First_Name, ' ', m.Last_Name) AS Athlete_Name,
                   c.Country_Code, t.Country,
                   t.Last_Score, t.Score, t.Dev, t.Races, t.Tour_Points, t.Total
              FROM TWA_Ranking t
              JOIN Ranked_In   ri ON ri.Ranking_ID  = t.Ranking_ID
              JOIN Athletes    a  ON a.Athlete_ID   = ri.Athlete_ID
              JOIN Members     m  ON m.Member_ID    = a.Member_ID
              JOIN Country     c  ON c.Country_Name = t.Country
             WHERE t.Gender = %s
               AND (%s IS NULL OR t.Country = %s)
             ORDER BY t.Ranking, t.Score DESC, Athlete_Name
             LIMIT %s
            """,
            (gender, country, country, limit),
        )
