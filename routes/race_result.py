from fastapi import APIRouter

from base_models.race_result import RaceResult
from database_api import race_result

router = APIRouter(prefix="/race-result", tags=["Race Result"])


@router.post("")
def add_race_result(result_info: RaceResult):
    race_result.add_race_result(
        result_info.athlete_id,
        result_info.race_id,
        result_info.place,
        result_info.finish_time,
        result_info.category,
        result_info.points,
    )
    return {"result": "successfully added race result"}


@router.delete("/{athlete_id}/{race_id}")
def delete_race_result(athlete_id: str, race_id: int):
    race_result.delete_race_result(athlete_id, race_id)
    return {"result": "successfully deleted race result"}


@router.put("")
def update_race_result(result_info: RaceResult):
    race_result.update_race_result(
        result_info.athlete_id,
        result_info.race_id,
        result_info.place,
        result_info.finish_time,
        result_info.category,
        result_info.points,
    )
    return {"result": "successfully updated race result"}


@router.get("/{athlete_id}/{race_id}")
def get_race_result(athlete_id: str, race_id: int):
    output = race_result.get_race_result(athlete_id, race_id)
    return {"result": output}
