from fastapi import APIRouter

from base_models.members import Member, MemberUpdate
from database_api import members

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("")
def add_member(member: Member):
    members.add_member(member.first_name, member.last_name)
    return {"result": "successfully added member"}


@router.delete("/{member_id}")
def delete_member(member_id: int):
    members.delete_member(member_id)
    return {"result": "successfully deleted member"}


@router.put("")
def update_member(member: MemberUpdate):
    members.update_member(member.member_id, member.first_name, member.last_name)
    return {"result": "successfully updated member"}


@router.get("/{member_id}")
def get_member(member_id: int):
    output = members.get_member(member_id)
    return {"result": output}
