from pydantic import BaseModel


class Statistics(BaseModel):
    stat_rank: int
    score: float
    country_name: str


class StatisticsUpdate(Statistics):
    stat_id: int
