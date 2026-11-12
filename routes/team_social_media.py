from fastapi import APIRouter

from base_models.team_social_media import TeamSocialMedia, TeamSocialMediaUpdate
from database_api import team_social_media

router = APIRouter(prefix="/team-social-media", tags=["Team Social Media"])


@router.post("")
def add_team_social_media(social_media_info: TeamSocialMedia):
    team_social_media.add_team_social_media(
        social_media_info.member_id, social_media_info.social_media_handle
    )
    return {"result": "successfully added team social media"}


@router.delete("/{member_id}/{social_media_handle}")
def delete_team_social_media(member_id: int, social_media_handle: str):
    team_social_media.delete_team_social_media(member_id, social_media_handle)
    return {"result": "successfully deleted team social media"}


@router.put("")
def update_team_social_media(social_media_info: TeamSocialMediaUpdate):
    team_social_media.update_team_social_media(
        social_media_info.member_id,
        social_media_info.social_media_handle,
        social_media_info.new_social_media_handle,
    )
    return {"result": "successfully updated team social media"}


@router.get("/{member_id}/{social_media_handle}")
def get_team_social_media(member_id: int, social_media_handle: str):
    output = team_social_media.get_team_social_media(
        member_id, social_media_handle
    )
    return {"result": output}
