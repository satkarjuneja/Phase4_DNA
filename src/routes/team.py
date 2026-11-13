from fastapi import APIRouter

from base_models.team import Team
from database_api import team

router = APIRouter(prefix="/team", tags=["Team"])


@router.post("")
def add_team(team_info: Team):
    team.add_team(
        team_info.member_id,
        team_info.role,
        team_info.country_name,
        team_info.description,
    )
    return {"result": "successfully added team"}


@router.delete("/{member_id}")
def delete_team(member_id: int):
    team.delete_team(member_id)
    return {"result": "successfully deleted team"}


@router.put("")
def update_team(team_info: Team):
    team.update_team(
        team_info.member_id,
        team_info.role,
        team_info.country_name,
        team_info.description,
    )
    return {"result": "successfully updated team"}


@router.get("/{member_id}")
def get_team(member_id: int):
    output = team.get_team(member_id)
    return {"result": output}
