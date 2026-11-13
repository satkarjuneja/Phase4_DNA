from fastapi import APIRouter

from base_models.venue import Venue
from database_api import venue

router = APIRouter(prefix="/venue", tags=["Venue"])


@router.post("")
def add_venue(venue_info: Venue):
    venue.add_venue(
        venue_info.country_name,
        venue_info.name,
        venue_info.number_of_stairs,
        venue_info.city,
        venue_info.special_info,
        venue_info.street,
        venue_info.postal_code,
    )
    return {"result": "successfully added venue"}


@router.delete("/{country_name}/{name}")
def delete_venue(country_name: str, name: str):
    venue.delete_venue(country_name, name)
    return {"result": "successfully deleted venue"}


@router.put("")
def update_venue(venue_info: Venue):
    venue.update_venue(
        venue_info.country_name,
        venue_info.name,
        venue_info.number_of_stairs,
        venue_info.city,
        venue_info.special_info,
        venue_info.street,
        venue_info.postal_code,
    )
    return {"result": "successfully updated venue"}


@router.get("")
def list_venues(country: str | None = None, min_stairs: int | None = None):
    """Venue directory with races hosted, last and next race."""
    return {"result": venue.list_venues(country, min_stairs)}


@router.get("/{country_name}/{name}")
def get_venue(country_name: str, name: str):
    output = venue.get_venue(country_name, name)
    return {"result": output}
