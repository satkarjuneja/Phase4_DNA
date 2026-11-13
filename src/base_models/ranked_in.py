from pydantic import BaseModel


class RankedIn(BaseModel):
    athlete_id: str
    ranking_id: int


class RankedInUpdate(RankedIn):
    new_athlete_id: str
    new_ranking_id: int
