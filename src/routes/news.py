from datetime import date

from fastapi import APIRouter

from base_models.news import News
from database_api import news

router = APIRouter(prefix="/news", tags=["News"])


@router.post("")
def add_news(news_info: News):
    news.add_news(
        news_info.member_id,
        news_info.news_date,
        news_info.title,
        news_info.text,
        news_info.category,
    )
    return {"result": "successfully added news"}


@router.delete("/{member_id}/{news_date}/{title:path}")
def delete_news(member_id: int, news_date: date, title: str):
    news.delete_news(member_id, news_date, title)
    return {"result": "successfully deleted news"}


@router.put("")
def update_news(news_info: News):
    news.update_news(
        news_info.member_id,
        news_info.news_date,
        news_info.title,
        news_info.text,
        news_info.category,
    )
    return {"result": "successfully updated news"}


@router.get("/{member_id}/{news_date}/{title:path}")
def get_news(member_id: int, news_date: date, title: str):
    output = news.get_news(member_id, news_date, title)
    return {"result": output}
