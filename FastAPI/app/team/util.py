from datetime import datetime
from typing import Union
import uuid
from dateutil.relativedelta import relativedelta

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.error import error_detail
from fastapi import  status, Depends,HTTPException
from app.core.session import get_db

from app.opt.subscription.model import BillingCycle, Plan
from app.team.model import Team, TeamInvitation, TeamParticipation


def get_team_member_count(team_id, db: Session = Depends(get_db)):

    count_query = (
        db.query(TeamParticipation)
        .with_entities(func.count().label("count"))
        .filter(
            TeamParticipation.is_admin == False,
            TeamParticipation.team_id == team_id,
        )
    )
    return count_query.scalar()


def check_team_member_count_or_406(team_id, number_of_licenses):
    seat_user_count = get_team_member_count(team_id)
    if number_of_licenses < seat_user_count:
        print("(bc0c)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("MEMBER_COUNT_WOULD_BE_MORE_THAN_LICENSE_COUNT_II")
        )


# get user teams: kullanıcının takımlarını döndürür
def get_user_participations(user_id, db: Session = Depends(get_db)):
    query = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.user_id == user_id,
            TeamParticipation.is_admin == False,
        )
        .all()
    )
    return query


def get_user_participation_count(user_id, db: Session = Depends(get_db)):
    return (
        db.query(func.count(TeamParticipation.created_at))
        .filter(
            TeamParticipation.user_id == user_id,
            TeamParticipation.is_admin == False,
        )
        .scalar()
    )
   
def get_admin_participation_count(user_id, db: Session = Depends(get_db)):
    return (
        db.query(func.count(TeamParticipation.created_at))
        .filter(
            TeamParticipation.user_id == user_id,
            TeamParticipation.is_admin == True,
        )
        .scalar()
    )
   
def get_participation_count(user_id, db: Session = Depends(get_db))->Union[int,None]:
    return (
        db.query(func.count(TeamParticipation.created_at))
        .filter(
            TeamParticipation.user_id == user_id
        )
        .scalar()
    )
    
def get_invitation_count(email, db: Session = Depends(get_db))->Union[int,None]:
    return (
        db.query(func.count(TeamInvitation.created_at))
        .filter(
            TeamInvitation.email==email
        )
        .scalar()
    )
   
def get_user_lastest_term_end(user_id, db: Session = Depends(get_db)):
    participiants = get_user_participations(user_id, db)
    if not participiants:
        return 0
    team_ids = []
    for value in participiants:
        team_ids.append(value.team_id)
    query = (
        db.query(Team)
        .filter(Team.id.in_(team_ids))
        .order_by(Team.term_end_date.desc())
        .first()
    )
    return query.term_end_date

