from datetime import date

from pydantic import BaseModel


class News(BaseModel):
    member_id: int
    news_date: date
    title: str
    text: str
    category: str | None = None
