from .db import get_db


def add_team_social_media(member_id: int, social_media_handle: str):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO Team_Social_Media (Member_ID, Social_Media_Handle)
            VALUES (?, ?)
            """,
            (member_id, social_media_handle),
        )


def delete_team_social_media(member_id: int, social_media_handle: str):
    with get_db() as db:
        db.execute(
            """
            DELETE FROM Team_Social_Media
             WHERE Member_ID = ? AND Social_Media_Handle = ?
            """,
            (member_id, social_media_handle),
        )


def update_team_social_media(
    member_id: int, social_media_handle: str, new_social_media_handle: str
):
    with get_db() as db:
        db.execute(
            """
            UPDATE Team_Social_Media
               SET Social_Media_Handle = ?
             WHERE Member_ID = ? AND Social_Media_Handle = ?
            """,
            (new_social_media_handle, member_id, social_media_handle),
        )


def get_team_social_media(member_id: int, social_media_handle: str):
    with get_db() as db:
        cur = db.execute(
            """
            SELECT * FROM Team_Social_Media
             WHERE Member_ID = ? AND Social_Media_Handle = ?
            """,
            (member_id, social_media_handle),
        )
        return cur.fetchone()


def get_team_social_media_by_team(member_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM Team_Social_Media WHERE Member_ID = ?",
            (member_id,),
        )
        return cur.fetchall()
