from fastapi import APIRouter

from base_models.tour import Tour
from database_api import tour

router = APIRouter(prefix="/tour", tags=["Tour"])


@router.post("")
def add_tour(tour_info: Tour):
    tour.add_tour(tour_info.year, tour_info.tour_name)
    return {"result": "successfully added tour"}


@router.delete("/{year}")
def delete_tour(year: int):
    tour.delete_tour(year)
    return {"result": "successfully deleted tour"}


@router.put("")
def update_tour(tour_info: Tour):
    tour.update_tour(tour_info.year, tour_info.tour_name)
    return {"result": "successfully updated tour"}


@router.get("/{year}")
def get_tour(year: int):
    output = tour.get_tour(year)
    return {"result": output}
