from fastapi import APIRouter

from base_models.twa_ranking import TWARanking, TWARankingUpdate
from database_api import twa_ranking

router = APIRouter(prefix="/twa-ranking", tags=["TWA Ranking"])


@router.post("")
def add_twa_ranking(ranking_info: TWARanking):
    twa_ranking.add_twa_ranking(
        ranking_info.country,
        ranking_info.ranking,
        ranking_info.score,
        ranking_info.gender,
        ranking_info.d_plus_minus,
        ranking_info.last_score,
        ranking_info.races,
        ranking_info.tour_points,
    )
    return {"result": "successfully added TWA ranking"}


@router.delete("/{ranking_id}")
def delete_twa_ranking(ranking_id: int):
    twa_ranking.delete_twa_ranking(ranking_id)
    return {"result": "successfully deleted TWA ranking"}


@router.put("")
def update_twa_ranking(ranking_info: TWARankingUpdate):
    twa_ranking.update_twa_ranking(
        ranking_info.ranking_id,
        ranking_info.country,
        ranking_info.ranking,
        ranking_info.score,
        ranking_info.gender,
        ranking_info.d_plus_minus,
        ranking_info.last_score,
        ranking_info.races,
        ranking_info.tour_points,
    )
    return {"result": "successfully updated TWA ranking"}


@router.get("")
def get_ranking_table(gender: str = "Male", country: str | None = None):
    """TWA world ranking for one gender (optionally one country), best first."""
    return {"result": twa_ranking.get_ranking_table(gender, country)}


@router.get("/{ranking_id}")
def get_twa_ranking(ranking_id: int):
    output = twa_ranking.get_twa_ranking(ranking_id)
    return {"result": output}
