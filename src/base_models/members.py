from pydantic import BaseModel


class Member(BaseModel):
    first_name: str
    last_name: str


class MemberUpdate(Member):
    member_id: int
