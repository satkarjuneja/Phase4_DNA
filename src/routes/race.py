from fastapi import APIRouter

from base_models.race import Race, RaceUpdate
from database_api import race

router = APIRouter(prefix="/race", tags=["Race"])


@router.post("")
def add_race(race_info: Race):
    race_id = race.add_race(
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
    return {"result": "successfully added race", "race_id": race_id}


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


@router.get("")
def list_races(
    status: str | None = None,
    year: int | None = None,
    country: str | None = None,
    factor: int | None = None,
    month: str | None = None,
    search: str | None = None,
    tour_year: int | None = None,
    venue: str | None = None,
):
    """Race calendar. status = 'upcoming' or 'past'; month = 'YYYY-MM'."""
    return {
        "result": race.list_races(status, year, country, factor, month, search, tour_year, venue)
    }


@router.get("/months")
def list_race_months():
    """Months that have races (the "Events by month" links)."""
    return {"result": race.list_race_months()}


@router.get("/{race_id}/results")
def get_race_results(race_id: int, category: str | None = None):
    """Race details with its results table (optionally one category)."""
    return {"result": race.get_race_results(race_id, category)}


@router.get("/{race_id}/editions")
def get_race_editions(race_id: int):
    """Every edition of this race (previous and later) with its winners."""
    return {"result": race.get_race_editions(race_id)}


@router.get("/{race_id}")
def get_race(race_id: int):
    output = race.get_race(race_id)
    return {"result": output}
