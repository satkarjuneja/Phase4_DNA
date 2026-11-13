from pydantic import BaseModel


class TeamSocialMedia(BaseModel):
    member_id: int
    social_media_handle: str


class TeamSocialMediaUpdate(TeamSocialMedia):
    new_social_media_handle: str
