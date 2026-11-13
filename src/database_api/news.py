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


# ---------------------------------------------------------------------------
# Functional requirement: news feed (the site's home and News pages), newest
# first, with the author's name and role; filterable by category and by a
# word in the title or text, and paged.
# ---------------------------------------------------------------------------
def list_news(
    category: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    check(1 <= limit <= 100, "Limit must be between 1 and 100")
    check(offset >= 0, "Offset cannot be negative")
    pattern = like_pattern(search)
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT n.`Date`, n.Title, n.`Text`, n.Category,
                   n.Member_ID, CONCAT(m.First_Name, ' ', m.Last_Name) AS Author,
                   t.Role AS Author_Role
              FROM News n
              JOIN Team    t ON t.Member_ID = n.Member_ID
              JOIN Members m ON m.Member_ID = n.Member_ID
             WHERE (%s IS NULL OR n.Category = %s)
               AND (%s IS NULL OR n.Title LIKE %s OR n.`Text` LIKE %s)
             ORDER BY n.`Date` DESC, n.Title
             LIMIT %s OFFSET %s
            """,
            (category, category, pattern, pattern, pattern, limit, offset),
        )


def count_news(category: str | None = None, search: str | None = None) -> int:
    pattern = like_pattern(search)
    with get_db() as db:
        row = db.execute(
            """
            SELECT COUNT(*) AS Total
              FROM News n
             WHERE (%s IS NULL OR n.Category = %s)
               AND (%s IS NULL OR n.Title LIKE %s OR n.`Text` LIKE %s)
            """,
            (category, category, pattern, pattern, pattern),
        ).fetchone()
        return row["Total"]


def list_categories():
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT Category, COUNT(*) AS Posts
              FROM News
             WHERE Category IS NOT NULL
             GROUP BY Category
             ORDER BY Category
            """
        )


def get_news_post(member_id: int, news_date, title: str):
    """One post with its author's name and role (news detail page)."""
    with get_db() as db:
        return db.fetch_one(
            """
            SELECT n.`Date`, n.Title, n.`Text`, n.Category, n.Member_ID,
                   CONCAT(m.First_Name, ' ', m.Last_Name) AS Author, t.Role AS Author_Role
              FROM News n
              JOIN Team    t ON t.Member_ID = n.Member_ID
              JOIN Members m ON m.Member_ID = n.Member_ID
             WHERE n.Member_ID = %s AND n.`Date` = %s AND n.Title = %s
            """,
            (member_id, news_date, title),
            f"News '{title}' ({news_date}) not found",
        )
