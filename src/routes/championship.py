from fastapi import APIRouter

from base_models.championship import Championship
from database_api import championship

router = APIRouter(prefix="/championship", tags=["Championship"])


@router.post("")
def add_championship(championship_info: Championship):
    championship.add_championship(
        championship_info.name, championship_info.year, championship_info.level
    )
    return {"result": "successfully added championship"}


@router.delete("/{name}/{year}")
def delete_championship(name: str, year: int):
    championship.delete_championship(name, year)
    return {"result": "successfully deleted championship"}


@router.put("")
def update_championship(championship_info: Championship):
    championship.update_championship(
        championship_info.name, championship_info.year, championship_info.level
    )
    return {"result": "successfully updated championship"}


@router.get("")
def list_championships(level: str | None = None):
    """Championships by year with the race each was held at."""
    return {"result": championship.list_championships(level)}


@router.get("/{name}/{year}")
def get_championship(name: str, year: int):
    output = championship.get_championship(name, year)
    return {"result": output}
