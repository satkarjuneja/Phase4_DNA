from datetime import date

from pydantic import BaseModel


class Race(BaseModel):
    race_name: str
    race_date: date
    edition_number: int
    factor: int
    venue_country: str
    venue_name: str
    race_link: str | None = None
    last_factor: int | None = None
    result_link: str | None = None
    result_link_old: str | None = None
    category: str | None = None
    additional_info: str | None = None
    previous_race_id: int | None = None
    tour_year: int | None = None
    position: int | None = None
    championship_name: str | None = None
    championship_year: int | None = None


class RaceUpdate(Race):
    race_id: int
