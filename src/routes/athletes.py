from fastapi import APIRouter

from base_models.athletes import Athlete, AthleteProfileUpdate, AthleteRegistration
from database_api import athletes

router = APIRouter(prefix="/athletes", tags=["Athletes"])


@router.post("")
def add_athlete(athlete_info: Athlete):
    athletes.add_athlete(
        athlete_info.athlete_id,
        athlete_info.member_id,
        athlete_info.email_address,
        athlete_info.phone_number,
        athlete_info.date_of_birth,
        athlete_info.gender,
        athlete_info.country_name,
        athlete_info.company_name,
        athlete_info.street,
        athlete_info.city,
        athlete_info.postal_code,
    )
    return {"result": "successfully added athlete"}


@router.delete("/{athlete_id}")
def delete_athlete(athlete_id: str):
    athletes.delete_athlete(athlete_id)
    return {"result": "successfully deleted athlete"}


@router.put("")
def update_athlete(athlete_info: Athlete):
    athletes.update_athlete(
        athlete_info.athlete_id,
        athlete_info.member_id,
        athlete_info.email_address,
        athlete_info.phone_number,
        athlete_info.date_of_birth,
        athlete_info.gender,
        athlete_info.country_name,
        athlete_info.company_name,
        athlete_info.street,
        athlete_info.city,
        athlete_info.postal_code,
    )
    return {"result": "successfully updated athlete"}


@router.post("/register")
def register_athlete(info: AthleteRegistration):
    """Create the member and the athlete in one transaction."""
    member_id = athletes.register_athlete(
        info.first_name, info.last_name, info.athlete_id, info.email_address,
        info.phone_number, info.date_of_birth, info.gender, info.country_name,
        info.company_name, info.street, info.city, info.postal_code,
    )
    return {"result": "successfully registered athlete", "member_id": member_id}


@router.put("/{athlete_id}/profile")
def update_athlete_profile(athlete_id: str, info: AthleteProfileUpdate):
    """Edit name, contact details and address."""
    athletes.update_athlete_profile(
        athlete_id, info.first_name, info.last_name, info.email_address,
        info.phone_number, info.company_name, info.street, info.city, info.postal_code,
    )
    return {"result": "successfully updated athlete profile"}


@router.delete("/{athlete_id}/registration")
def unregister_athlete(athlete_id: str):
    """Delete the athlete and the member record behind it."""
    athletes.unregister_athlete(athlete_id)
    return {"result": "successfully deleted athlete"}


@router.get("")
def search_athletes(
    search: str | None = None,
    country: str | None = None,
    gender: str | None = None,
):
    """Search athletes by name or Athlete ID, with results summary."""
    return {"result": athletes.search_athletes(search, country, gender)}


@router.get("/{athlete_id}/profile")
def get_athlete_profile(athlete_id: str):
    """Athlete profile: personal data, age, race history, registrations."""
    return {"result": athletes.get_athlete_profile(athlete_id)}


@router.get("/{athlete_id}")
def get_athlete(athlete_id: str):
    output = athletes.get_athlete(athlete_id)
    return {"result": output}
