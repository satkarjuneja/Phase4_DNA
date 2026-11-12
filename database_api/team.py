from .db import get_db

_ROLES = ("President", "Sports Director", "Association Representative")


def add_team(
    member_id: int,
    role: str,
    country_name: str,
    description: str | None = None,
):
    assert role in _ROLES
    with get_db() as db:
        assert (
            db.execute(
                "SELECT 1 FROM Athletes WHERE Member_ID = %s", (member_id,)
            ).fetchone()
            is None
        ), "Member is already an Athlete"
        db.execute(
            """
            INSERT INTO Team (Member_ID, Role, Description, Country_Name)
            VALUES (%s, %s, %s, %s)
            """,
            (member_id, role, description, country_name),
        )


def delete_team(member_id: int):
    with get_db() as db:
        db.execute("DELETE FROM Team WHERE Member_ID = %s", (member_id,))


def update_team(
    member_id: int,
    role: str,
    country_name: str,
    description: str | None = None,
):
    assert role in _ROLES
    with get_db() as db:
        db.execute(
            """
            UPDATE Team
               SET Role = %s, Description = %s, Country_Name = %s
             WHERE Member_ID = %s
            """,
            (role, description, country_name, member_id),
        )


def get_team(member_id: int):
    with get_db() as db:
        cur = db.execute("SELECT * FROM Team WHERE Member_ID = %s", (member_id,))
        return cur.fetchone()
