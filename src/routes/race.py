from fastapi import APIRouter

from base_models.race import Race, RaceUpdate
from database_api import race

router = APIRouter(prefix="/race", tags=["Race"])


@router.post("")
def add_race(race_info: Race):
    race.add_race(
        race_info.race_name,
        race_info.race_date,
        race_info.edition_number,
        race_info.factor,
        race_info.venue_country,
        race_info.venue_name,
        race_info.race_link,
        race_info.last_factor,
        race_info.result_link,
        race_info.result_link_old,
        race_info.category,
        race_info.additional_info,
        race_info.previous_race_id,
        race_info.tour_year,
        race_info.position,
        race_info.championship_name,
        race_info.championship_year,
    )
    return {"result": "successfully added race"}


@router.delete("/{race_id}")
def delete_race(race_id: int):
    race.delete_race(race_id)
    return {"result": "successfully deleted race"}


@router.put("")
def update_race(race_info: RaceUpdate):
    race.update_race(
        race_info.race_id,
        race_info.race_name,
        race_info.race_date,
        race_info.edition_number,
        race_info.factor,
        race_info.venue_country,
        race_info.venue_name,
        race_info.race_link,
        race_info.last_factor,
        race_info.result_link,
        race_info.result_link_old,
        race_info.category,
        race_info.additional_info,
        race_info.previous_race_id,
        race_info.tour_year,
        race_info.position,
        race_info.championship_name,
        race_info.championship_year,
    )
    return {"result": "successfully updated race"}


@router.get("/{race_id}")
def get_race(race_id: int):
    output = race.get_race(race_id)
    return {"result": output}
