from pydantic import BaseModel


class Team(BaseModel):
    member_id: int
    role: str
    country_name: str
    description: str | None = None
