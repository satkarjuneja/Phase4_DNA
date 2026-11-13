from fastapi import APIRouter

from base_models.country import Country
from database_api import country

router = APIRouter(prefix="/country", tags=["Country"])


@router.post("")
def add_country(country_info: Country):
    country.add_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully added country"}


@router.delete("/{country_name}")
def delete_country(country_name: str):
    country.delete_country(country_name)
    return {"result": "successfully deleted country"}


@router.put("")
def update_country(country_info: Country):
    country.update_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully updated country"}


@router.get("/{country_name}")
def get_country(country_name: str):
    output = country.get_country(country_name)
    return {"result": output}
