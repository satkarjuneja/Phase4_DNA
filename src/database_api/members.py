from .db import get_db
from .errors import check


def add_member(first_name: str, last_name: str):
    check(first_name.strip() and last_name.strip(), "First and last name are required")
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO Members (First_Name, Last_Name) VALUES (%s, %s)",
            (first_name, last_name),
        )
        return cur.lastrowid


def delete_member(member_id: int):
    with get_db() as db:
        db.modify(
            "DELETE FROM Members WHERE Member_ID = %s",
            (member_id,),
            f"Member {member_id} not found",
        )


def update_member(member_id: int, first_name: str, last_name: str):
    check(first_name.strip() and last_name.strip(), "First and last name are required")
    with get_db() as db:
        db.modify(
            "UPDATE Members SET First_Name = %s, Last_Name = %s WHERE Member_ID = %s",
            (first_name, last_name, member_id),
            f"Member {member_id} not found",
        )


def get_member(member_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Members WHERE Member_ID = %s",
            (member_id,),
            f"Member {member_id} not found",
        )
