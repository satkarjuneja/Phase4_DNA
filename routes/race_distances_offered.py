from fastapi import APIRouter

from base_models.race_distances_offered import RaceDistance, RaceDistanceUpdate
from database_api import race_distances_offered

router = APIRouter(
    prefix="/race-distances-offered", tags=["Race Distances Offered"]
)


@router.post("")
def add_race_distance(distance_info: RaceDistance):
    race_distances_offered.add_race_distance(
        distance_info.race_id, distance_info.distance
    )
    return {"result": "successfully added race distance"}


@router.delete("/{race_id}/{distance}")
def delete_race_distance(race_id: int, distance: str):
    race_distances_offered.delete_race_distance(race_id, distance)
    return {"result": "successfully deleted race distance"}


@router.put("")
def update_race_distance(distance_info: RaceDistanceUpdate):
    race_distances_offered.update_race_distance(
        distance_info.race_id, distance_info.distance, distance_info.new_distance
    )
    return {"result": "successfully updated race distance"}


@router.get("/{race_id}/{distance}")
def get_race_distance(race_id: int, distance: str):
    output = race_distances_offered.get_race_distance(race_id, distance)
    return {"result": output}
