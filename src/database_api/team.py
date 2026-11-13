from .db import get_db
from .errors import ConflictError, check

_ROLES = ("President", "Sports Director", "Association Representative")


def add_team(
    member_id: int,
    role: str,
    country_name: str,
    description: str | None = None,
):
    check(role in _ROLES, f"Role must be one of: {', '.join(_ROLES)}")
    with get_db() as db:
        if db.execute(
            "SELECT 1 FROM Athletes WHERE Member_ID = %s", (member_id,)
        ).fetchone():
            raise ConflictError(
                f"Member {member_id} is already an athlete and cannot also be a team member"
            )
        db.execute(
            """
            INSERT INTO Team (Member_ID, Role, Description, Country_Name)
            VALUES (%s, %s, %s, %s)
            """,
            (member_id, role, description, country_name),
        )


def delete_team(member_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Team WHERE Member_ID = %s",
            (member_id,),
            f"Team member {member_id} not found",
        )


def update_team(
    member_id: int,
    role: str,
    country_name: str,
    description: str | None = None,
):
    check(role in _ROLES, f"Role must be one of: {', '.join(_ROLES)}")
    with get_db() as db:
        db.modify(
            """
            UPDATE Team
               SET Role = %s, Description = %s, Country_Name = %s
             WHERE Member_ID = %s
            """,
            (role, description, country_name, member_id),
            f"Team member {member_id} not found",
        )


def get_team(member_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Team WHERE Member_ID = %s",
            (member_id,),
            f"Team member {member_id} not found",
        )


# ---------------------------------------------------------------------------
# Functional requirement: "Our Team" page -- every team member with name,
# role, country, social media links and number of news posts. LEFT JOINs
# keep members without social media or posts. Presidium roles come first.
# ---------------------------------------------------------------------------
def list_team():
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT t.Member_ID, m.First_Name, m.Last_Name, t.Role, t.Description,
                   t.Country_Name, c.Country_Code,
                   (SELECT GROUP_CONCAT(s.Social_Media_Handle ORDER BY s.Social_Media_Handle SEPARATOR ' ')
                      FROM Team_Social_Media s
                     WHERE s.Member_ID = t.Member_ID)                       AS Social_Media,
                   (SELECT COUNT(*) FROM News n WHERE n.Member_ID = t.Member_ID) AS News_Posts
              FROM Team t
              JOIN Members m ON m.Member_ID    = t.Member_ID
              JOIN Country c ON c.Country_Name = t.Country_Name
             ORDER BY FIELD(t.Role, 'President', 'Sports Director', 'Association Representative'),
                      t.Country_Name, m.Last_Name
            """
        )
