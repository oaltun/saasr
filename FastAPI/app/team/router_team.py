
import uuid
from app.core.schema import ErrorDetail

from app.team import schema
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user_or_400
from app.core.session import get_db


from app.team.model import Team
from app.user.model import User


from app.team.crud import (
    create_team,
    team_check_number_of_licenses_or_406,
    team_check_team_name_or_406,
    team_user_is_admin_or_403,
    db_get_item_or_404,
)

team_router = router = APIRouter(prefix="/teams")



# Create endpoint---------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.TeamOut,
    responses={
        400: {"model": ErrorDetail },
    },
    description="create team and set its first admin",
)
def team_create(
    input: schema.TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    return create_team(input.dict(),current_user,db)




# Read one endpoint --------------------------------------------------
@router.get(
    "/{id}", 
    response_model=schema.TeamOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

)
def team_get(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    team: Team = db_get_item_or_404(id, Team, "Team", db)
    team_user_is_admin_or_403(current_user.id, team_id=team.id, db=db)
    return team




# Update endpoint-------------------------------------------------------
@router.put(
    "/{id}",
    response_model=schema.TeamOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
    }
)
def team_update(
    id: uuid.UUID,
    update: schema.TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    team: Team = db_get_item_or_404(id, Team, "Team", db)
    team_user_is_admin_or_403(current_user.id, id, db)

    if update.number_of_licenses_next_term is not None:
        team_check_number_of_licenses_or_406(update.number_of_licenses_next_term)

    if update.name is not None:
        team_check_team_name_or_406(update.name)

    ## do the update

    # get rid of all '=None'
    update_dict = {k: v for k, v in update.dict().items() if v is not None}

    # update
    db.query(Team).filter(Team.id == id).update(
        update_dict, synchronize_session=False
    )
    db.commit()

    ## return updated team
    return db_get_item_or_404(id, Team, "Team", db)
