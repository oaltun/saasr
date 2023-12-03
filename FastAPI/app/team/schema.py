import uuid
from app.opt.subscription.schema import BillingCycle, PlanOut
from pydantic import BaseModel, EmailStr,NoneStr
from datetime import datetime
from typing import Optional, List

from app.user.schema import UserOutFull, UserOutMailNames


class TeamParticipationUpdate:
    is_admin: Optional[bool] = None
    recurring_payer: Optional[bool] = None


class TeamParticipationCreate(BaseModel):
    team_id: uuid.UUID
    user_id: uuid.UUID
    is_admin: bool
    recurring_payer: bool

    class Config:
        orm_mode = True





class TeamInvitationBase(BaseModel):
    pass


class TeamInvitationCreate(TeamInvitationBase):
    team_id: uuid.UUID
    email: EmailStr
    is_admin: bool


class TeamInvitationStatusUpdate(TeamInvitationBase):
    team_id: uuid.UUID
    is_accept: bool





class TeamInvitationDelete(TeamInvitationBase):
    id: uuid.UUID
    is_accept: bool = True


class TeamBase(BaseModel):
    number_of_licenses_next_term: Optional[int] = 0
    recurring_billing_is_on: bool
    name: str


class TeamCreate(BaseModel):
    pass


class TeamOutInList(TeamBase):
    id: uuid.UUID
    created_at = datetime
    plan_id: Optional[str] = None
    billing_cycle_id: Optional[str] = None
    billing_cycle_id_next_term: Optional[str] = None
    name: str
    number_of_licenses: int
    number_of_licenses_next_term: int
    recurring_billing_is_on: bool
    term_end_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class TeamOutSimple(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        orm_mode = True

class TeamInvitationOut(TeamInvitationBase):
    id: uuid.UUID
    email: EmailStr
    is_admin: bool
    team: TeamOutSimple
    inviter: UserOutMailNames

    class Config:
        orm_mode = True
        
class TeamParticipationOut(TeamParticipationCreate):
    created_at: datetime
    # user: List[UserOut]
    team: TeamOutInList
    user: UserOutFull

    class Config:
        orm_mode = True

class TeamOut(TeamOutInList):
    invitations: List[TeamInvitationOut] = []
    participations: List[TeamParticipationOut] = []
    plan: Optional[PlanOut]
    billing_cycle: Optional[BillingCycle]

    class Config:
        orm_mode = True






class TeamUpdate(TeamBase):
    name: NoneStr = None
    number_of_licenses_next_term: int = None
    recurring_billing_is_on: bool = None
