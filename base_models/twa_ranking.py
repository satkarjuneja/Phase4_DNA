from pydantic import BaseModel


class TWARanking(BaseModel):
    country: str
    ranking: int
    score: float
    gender: str
    d_plus_minus: str | None = None
    last_score: float | None = None
    races: int = 0
    tour_points: float = 0


class TWARankingUpdate(TWARanking):
    ranking_id: int
