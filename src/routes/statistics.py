from fastapi import APIRouter

from base_models.statistics import Statistics, StatisticsUpdate
from database_api import statistics

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.post("")
def add_statistics(statistics_info: Statistics):
    statistics.add_statistics(
        statistics_info.stat_rank,
        statistics_info.score,
        statistics_info.country_name,
    )
    return {"result": "successfully added statistics"}


@router.delete("/{stat_id}")
def delete_statistics(stat_id: int):
    statistics.delete_statistics(stat_id)
    return {"result": "successfully deleted statistics"}


@router.put("")
def update_statistics(statistics_info: StatisticsUpdate):
    statistics.update_statistics(
        statistics_info.stat_id,
        statistics_info.stat_rank,
        statistics_info.score,
        statistics_info.country_name,
    )
    return {"result": "successfully updated statistics"}


@router.get("/countries")
def get_country_standings(gender: str | None = None):
    """Nations table: points and medals per country."""
    return {"result": statistics.get_country_standings(gender)}


@router.get("/{stat_id}")
def get_statistics(stat_id: int):
    output = statistics.get_statistics(stat_id)
    return {"result": output}
