from .db import get_db


def add_member(first_name: str, last_name: str):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO Members (First_Name, Last_Name) VALUES (%s, %s)",
            (first_name, last_name),
        )
        return cur.lastrowid


def delete_member(member_id: int):
    with get_db() as db:
        db.execute("DELETE FROM Members WHERE Member_ID = %s", (member_id,))


def update_member(member_id: int, first_name: str, last_name: str):
    with get_db() as db:
        db.execute(
            "UPDATE Members SET First_Name = %s, Last_Name = %s WHERE Member_ID = %s",
            (first_name, last_name, member_id),
        )


def get_member(member_id: int):
    with get_db() as db:
        cur = db.execute("SELECT * FROM Members WHERE Member_ID = %s", (member_id,))
        return cur.fetchone()
