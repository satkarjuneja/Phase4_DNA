from pydantic import BaseModel


class RaceDistance(BaseModel):
    race_id: int
    distance: str


class RaceDistanceUpdate(RaceDistance):
    new_distance: str
