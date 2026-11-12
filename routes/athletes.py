from fastapi import APIRouter

from base_models.athletes import Athlete
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


@router.get("/{athlete_id}")
def get_athlete(athlete_id: str):
    output = athletes.get_athlete(athlete_id)
    return {"result": output}
