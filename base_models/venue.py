from pydantic import BaseModel


class Venue(BaseModel):
    country_name: str
    name: str
    number_of_stairs: int
    city: str
    special_info: str | None = None
    street: str | None = None
    postal_code: str | None = None
