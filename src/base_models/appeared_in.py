from pydantic import BaseModel


class AppearedIn(BaseModel):
    athlete_id: str
    race_id: int
    stat_id: int


class AppearedInUpdate(AppearedIn):
    new_athlete_id: str
    new_race_id: int
    new_stat_id: int
