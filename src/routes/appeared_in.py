from fastapi import APIRouter

from base_models.appeared_in import AppearedIn, AppearedInUpdate
from database_api import appeared_in

router = APIRouter(prefix="/appeared-in", tags=["Appeared In"])


@router.post("")
def add_appearance(appearance: AppearedIn):
    appeared_in.add_appeared_in(
        appearance.athlete_id, appearance.race_id, appearance.stat_id
    )
    return {"result": "successfully added appearance"}


@router.delete("/{athlete_id}/{race_id}/{stat_id}")
def delete_appearance(athlete_id: str, race_id: int, stat_id: int):
    appeared_in.delete_appeared_in(athlete_id, race_id, stat_id)
    return {"result": "successfully deleted appearance"}


@router.put("")
def update_appearance(appearance: AppearedInUpdate):
    if (
        appearance.athlete_id != appearance.new_athlete_id
        or appearance.race_id != appearance.new_race_id
        or appearance.stat_id != appearance.new_stat_id
    ):
        appeared_in.delete_appeared_in(
            appearance.athlete_id, appearance.race_id, appearance.stat_id
        )
        appeared_in.add_appeared_in(
            appearance.new_athlete_id, appearance.new_race_id, appearance.new_stat_id
        )
    return {"result": "successfully updated appearance"}


@router.get("/{athlete_id}/{race_id}/{stat_id}")
def get_appearance(athlete_id: str, race_id: int, stat_id: int):
    output = appeared_in.get_appeared_in(athlete_id, race_id, stat_id)
    return {"result": output}
