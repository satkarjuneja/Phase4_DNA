from pydantic import BaseModel


class RaceResult(BaseModel):
    athlete_id: str
    race_id: int
    place: int
    finish_time: str
    category: str
    points: float = 0
