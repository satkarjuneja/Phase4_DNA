from .db import get_db


def add_news(
    member_id: int,
    news_date: str,
    title: str,
    text: str,
    category: str | None = None,
):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO News (Member_ID, `Date`, Title, `Text`, Category)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (member_id, news_date, title, text, category),
        )


def delete_news(member_id: int, news_date: str, title: str):
    with get_db() as db:
        db.execute(
            'DELETE FROM News WHERE Member_ID = %s AND `Date` = %s AND Title = %s',
            (member_id, news_date, title),
        )


def update_news(
    member_id: int,
    news_date: str,
    title: str,
    text: str,
    category: str | None = None,
):
    with get_db() as db:
        db.execute(
            """
            UPDATE News
               SET `Text` = %s, Category = %s
             WHERE Member_ID = %s AND `Date` = %s AND Title = %s
            """,
            (text, category, member_id, news_date, title),
        )


def get_news(member_id: int, news_date: str, title: str):
    with get_db() as db:
        cur = db.execute(
            'SELECT * FROM News WHERE Member_ID = %s AND `Date` = %s AND Title = %s',
            (member_id, news_date, title),
        )
        return cur.fetchone()
