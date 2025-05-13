from dataclasses import dataclass
from abc import ABC


@dataclass(init=False)
class BaseDTO(ABC):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass(init=False)
class TeamDTO(BaseDTO):
    team_id: int
    name: str
    hexcode: str
    logo_path: str
    created_at: str
    active: bool
    team_captain_id: int
    team_role_id: int


@dataclass(init=False)
class TeamMemberDTO(BaseDTO):
    team_id: int
    user_id: int
    role: str
    team_display_name: str
    joined_at: str
    rating: int = None


@dataclass(init=False)
class UserDTO(BaseDTO):
    user_id: int
    username: str
    display_name: str
    joined_at: str
    is_roblox_verified: bool
    roblox_username: str
    rating: int = None
    position: str = None


@dataclass(init=False)
class TransactionDTO(BaseDTO):
    transaction_id: int
    team_id: int
    user_id: int
    action_type: str
    actor_id: int
    details: dict
    timestamp: str


@dataclass(init=False)
class InvitationDTO(BaseDTO):
    invitation_id: int
    team_id: int
    user_id: int
    inviter_id: int
    created_at: str
    expires_at: str
    status: str


@dataclass(init=False)
class GuildDTO(BaseDTO):
    id: int
    name: str
    owner_id: int
    prefix: str
    created_at: str
    updated_at: str
    settings: dict
    is_active: bool


@dataclass(init=False)
class ServerConfigDTO(BaseDTO):
    guild_id: int
    settings: dict
    updated_at: str
