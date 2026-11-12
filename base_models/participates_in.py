from pydantic import BaseModel


class ParticipatesIn(BaseModel):
    athlete_id: str
    race_id: int


class ParticipatesInUpdate(ParticipatesIn):
    new_athlete_id: str
    new_race_id: int
