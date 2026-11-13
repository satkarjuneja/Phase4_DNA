from .db import get_db
from .errors import check


def add_team_social_media(member_id: int, social_media_handle: str):
    check(social_media_handle.strip(), "Social media handle is required")
    with get_db() as db:
        db.execute(
            """
            INSERT INTO Team_Social_Media (Member_ID, Social_Media_Handle)
            VALUES (%s, %s)
            """,
            (member_id, social_media_handle),
        )


def delete_team_social_media(member_id: int, social_media_handle: str):
    with get_db() as db:
        db.modify(
            """
            DELETE FROM Team_Social_Media
             WHERE Member_ID = %s AND Social_Media_Handle = %s
            """,
            (member_id, social_media_handle),
            "Social media handle not found for this team member",
        )


def update_team_social_media(
    member_id: int, social_media_handle: str, new_social_media_handle: str
):
    check(new_social_media_handle.strip(), "New social media handle is required")
    with get_db() as db:
        db.modify(
            """
            UPDATE Team_Social_Media
               SET Social_Media_Handle = %s
             WHERE Member_ID = %s AND Social_Media_Handle = %s
            """,
            (new_social_media_handle, member_id, social_media_handle),
            "Social media handle not found for this team member",
        )


def get_team_social_media(member_id: int, social_media_handle: str):
    with get_db() as db:
        return db.fetch_one(
            """
            SELECT * FROM Team_Social_Media
             WHERE Member_ID = %s AND Social_Media_Handle = %s
            """,
            (member_id, social_media_handle),
            "Social media handle not found for this team member",
        )


def get_team_social_media_by_team(member_id: int):
    with get_db() as db:
        return db.fetch_all(
            "SELECT * FROM Team_Social_Media WHERE Member_ID = %s", (member_id,)
        )
