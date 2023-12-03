
import json
from app.opt.subscription.model import BillingCycle, Plan
from fastapi import  status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from fastapi import Depends, status

from app.team.model import Team, TeamInvitation, TeamParticipation
from app.team.schema import TeamParticipationCreate
from app.team import schema


def create_team(input_dict,current_user,db)->Team:
    new_team = Team(**input_dict)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # Add this user as an admin
    participation = participation_add(
        db,
        schema.TeamParticipationCreate(
            team_id=new_team.id,
            user_id=current_user.id,
            is_admin=True,
            recurring_payer=True,
        ),
    )

    return new_team

def team_get_member_count(team_id, db: Session) -> int:

    participation_count_query = (
        db.query(TeamParticipation)
        .with_entities(func.count().label("count"))
        .filter(
            TeamParticipation.is_admin == False,
            TeamParticipation.team_id == team_id,
        )
    )
    invitation_count_query = (
        db.query(TeamInvitation)
        .with_entities(func.count().label("count"))
        .filter(
            TeamInvitation.team_id == team_id,
            TeamInvitation.is_admin == False,
        )
    )
    participation_count = participation_count_query.scalar()
    invitation_count = invitation_count_query.scalar()
    return participation_count + invitation_count


def check_team_member_count_or_406(team_id, number_of_licenses, db: Session) -> bool:
    member_count = team_get_member_count(team_id, db)
    if number_of_licenses < member_count:
        print("(9128)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("MEMBER_COUNT_WOULD_BE_MORE_THAN_LICENSE_COUNT")
        )
    return True


def db_get_item_or_404(id, model, model_name, db: Session):

    item = db.query(model).filter(model.id == id).first()
    if item == None:
        print("(1285)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("DB_ITEM_DOES_NOT_EXIST_II")
        )
    return item


def db_item_exists_or_error(id, model, model_name, db: Session) -> bool:
    db_get_item_or_404(id, model, model_name, db)
    return True


def team_user_is_admin(user_id, team_id, db: Session) -> bool:

    team_admin = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.is_admin == True,
            TeamParticipation.team_id == team_id,
            TeamParticipation.user_id == user_id,
        )
        .first()
    )
    if not team_admin:
        return False
    else:
        return True


def team_user_is_admin_or_403(user_id, team_id, db: Session) -> bool:

    if not team_user_is_admin(user_id, team_id, db):
        print("(2856)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("USER_NOT_TEAM_ADMIN_V")
        )
    return True


def team_check_number_of_licenses_or_406(number_of_licenses):

    if number_of_licenses < 1:
        print("(a1ab)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("AT_LEAST_I_LICENCE_REQUIRED")
        )


from app.core.error import  error_detail
# from app.core.schema import ErrorCode,ErrorDetail
def team_check_team_name_or_406(name):
    if name=="":
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("TEAM_NAME_IS_EMPTY")
            
        )

def billing_cycle_exists_or_406(id, db: Session):

    billing_cycle = db_get_item_or_404(id, BillingCycle, "Billing Cycle", db)

    if not billing_cycle.is_active:
        print("(4f09)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("BILLING_CYCLE_IS_NOT_ACTIVE")
        )


def participation_add(db: Session, input: TeamParticipationCreate):

    p = TeamParticipation(**input.dict())
    db.add(p)
    db.commit()
    db.refresh(p)

    return p


