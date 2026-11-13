from fastapi import APIRouter

from base_models.participates_in import ParticipatesIn, ParticipatesInUpdate
from database_api import participates_in

router = APIRouter(prefix="/participates-in", tags=["Participates In"])


@router.post("")
def add_participation(participation: ParticipatesIn):
    participates_in.add_participates_in(
        participation.athlete_id, participation.race_id
    )
    return {"result": "successfully added participation"}


@router.delete("/{athlete_id}/{race_id}")
def delete_participation(athlete_id: str, race_id: int):
    participates_in.delete_participates_in(athlete_id, race_id)
    return {"result": "successfully deleted participation"}


@router.put("")
def update_participation(participation: ParticipatesInUpdate):
    if (
        participation.athlete_id != participation.new_athlete_id
        or participation.race_id != participation.new_race_id
    ):
        participates_in.delete_participates_in(
            participation.athlete_id, participation.race_id
        )
        participates_in.add_participates_in(
            participation.new_athlete_id, participation.new_race_id
        )
    return {"result": "successfully updated participation"}


@router.get("/{athlete_id}/{race_id}")
def get_participation(athlete_id: str, race_id: int):
    output = participates_in.get_participates_in(athlete_id, race_id)
    return {"result": output}
