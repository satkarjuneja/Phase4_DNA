from .db import get_db
from .errors import as_date, check, like_pattern


def add_news(
    member_id: int,
    news_date: str,
    title: str,
    text: str,
    category: str | None = None,
):
    as_date(news_date, "News date")
    check(title.strip(), "Title is required")
    check(text.strip(), "Text is required")
    with get_db() as db:
        db.execute(
            """
            INSERT INTO News (Member_ID, `Date`, Title, `Text`, Category)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (member_id, news_date, title, text, category),
        )


def delete_news(member_id: int, news_date: str, title: str):
    as_date(news_date, "News date")
    with get_db() as db:
        db.modify(
            "DELETE FROM News WHERE Member_ID = %s AND `Date` = %s AND Title = %s",
            (member_id, news_date, title),
            f"News '{title}' ({news_date}) not found",
        )


def update_news(
    member_id: int,
    news_date: str,
    title: str,
    text: str,
    category: str | None = None,
):
    as_date(news_date, "News date")
    check(text.strip(), "Text is required")
    with get_db() as db:
        db.modify(
            """
            UPDATE News
               SET `Text` = %s, Category = %s
             WHERE Member_ID = %s AND `Date` = %s AND Title = %s
            """,
            (text, category, member_id, news_date, title),
            f"News '{title}' ({news_date}) not found",
        )


def get_news(member_id: int, news_date: str, title: str):
    as_date(news_date, "News date")
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM News WHERE Member_ID = %s AND `Date` = %s AND Title = %s",
            (member_id, news_date, title),
            f"News '{title}' ({news_date}) not found",
        )
