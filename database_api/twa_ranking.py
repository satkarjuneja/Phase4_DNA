from .db import get_db

_GENDERS = ("Male", "Female")


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
    assert ranking > 0
    assert score >= 0
    assert last_score is None or last_score >= 0
    assert races >= 0
    assert tour_points >= 0
    assert gender in _GENDERS
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO TWA_Ranking
                (Country, Ranking, D_Plus_Minus, Last_Score, Score, Races, Tour_Points, Gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                country,
                ranking,
                d_plus_minus,
                last_score,
                score,
                races,
                tour_points,
                gender,
            ),
        )
        return cur.lastrowid


def delete_twa_ranking(ranking_id: int):
    with get_db() as db:
        db.execute("DELETE FROM TWA_Ranking WHERE Ranking_ID = ?", (ranking_id,))


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
    assert ranking > 0
    assert score >= 0
    assert last_score is None or last_score >= 0
    assert races >= 0
    assert tour_points >= 0
    assert gender in _GENDERS
    with get_db() as db:
        db.execute(
            """
            UPDATE TWA_Ranking
               SET Country = ?, Ranking = ?, D_Plus_Minus = ?, Last_Score = ?,
                   Score = ?, Races = ?, Tour_Points = ?, Gender = ?
             WHERE Ranking_ID = ?
            """,
            (
                country,
                ranking,
                d_plus_minus,
                last_score,
                score,
                races,
                tour_points,
                gender,
                ranking_id,
            ),
        )


def get_twa_ranking(ranking_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM TWA_Ranking WHERE Ranking_ID = ?", (ranking_id,)
        )
        return cur.fetchone()


def get_twa_rankings_by_gender(gender: str):
    assert gender in _GENDERS
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM TWA_Ranking WHERE Gender = ? ORDER BY Ranking",
            (gender,),
        )
        return cur.fetchall()
