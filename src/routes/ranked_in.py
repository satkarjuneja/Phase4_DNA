from fastapi import APIRouter

from base_models.ranked_in import RankedIn, RankedInUpdate
from database_api import ranked_in

router = APIRouter(prefix="/ranked-in", tags=["Ranked In"])


@router.post("")
def add_ranked_in(ranking: RankedIn):
    ranked_in.add_ranked_in(ranking.athlete_id, ranking.ranking_id)
    return {"result": "successfully added ranked-in entry"}


@router.delete("/{athlete_id}/{ranking_id}")
def delete_ranked_in(athlete_id: str, ranking_id: int):
    ranked_in.delete_ranked_in(athlete_id, ranking_id)
    return {"result": "successfully deleted ranked-in entry"}


@router.put("")
def update_ranked_in(ranking: RankedInUpdate):
    if (
        ranking.athlete_id != ranking.new_athlete_id
        or ranking.ranking_id != ranking.new_ranking_id
    ):
        ranked_in.delete_ranked_in(ranking.athlete_id, ranking.ranking_id)
        ranked_in.add_ranked_in(ranking.new_athlete_id, ranking.new_ranking_id)
    return {"result": "successfully updated ranked-in entry"}


@router.get("/{athlete_id}/{ranking_id}")
def get_ranked_in(athlete_id: str, ranking_id: int):
    output = ranked_in.get_ranked_in(athlete_id, ranking_id)
    return {"result": output}
