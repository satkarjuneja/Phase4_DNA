from pydantic import BaseModel


class Tour(BaseModel):
    year: int
    tour_name: str
