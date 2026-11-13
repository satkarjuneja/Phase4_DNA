from pydantic import BaseModel


class Championship(BaseModel):
    name: str
    year: int
    level: str
