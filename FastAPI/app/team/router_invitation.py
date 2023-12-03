import json
import uuid
from typing import Dict, List, Optional
from sqlalchemy import func, cast, TEXT
from app.core.crud import (
    add_limit_offset,
    add_order_by,
    add_search,
    fix_start_end,
    query_add_filter_sort_range_or_400,
)
from app.core.error import error_detail

from fastapi import (
    APIRouter,
    Depends,
    
    status,
    BackgroundTasks,
    Response,
    HTTPException
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user_or_400
from app.core.session import get_db

from app.team import schema
from app.team.model import Team, TeamInvitation, TeamParticipation
from app.user.model import User
from sqlalchemy import exc



from app.core.schema import EmailSchema, ErrorDetail
from fastapi_mail import MessageSchema

from app.team.crud import (
    team_user_is_admin,
    team_user_is_admin_or_403,
    db_get_item_or_404,
    team_get_member_count,
    participation_add,
)

from app.core.mail import send_mail_or_424
from app.user import html
from app.config import settings


invitation_router = router = APIRouter(prefix="/team_invitations")


@router.get(
    "",
    response_model=List[schema.TeamInvitationOut],
    description="Invitation List for the Current User. Returns the team invitations for the current user. If current user is super_user, returns all invitations.",
)
def invitation_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user_or_400),
):

    ### resource setup
    response_model = schema.TeamInvitationOut
    db_model = TeamInvitation
    text_fields = (
        cast(db_model.id, TEXT),
        db_model.email,
        cast(db_model.team_id, TEXT),
    )
    data_query = db.query(db_model)
    count_query = db.query(func.count(db_model.id))

    ### if not superuser, return invitations just for this person
    if not current_user.is_superuser:
        data_query = data_query.filter(
            TeamInvitation.email == current_user.email
        )
        count_query = count_query.filter(
            TeamInvitation.email == current_user.email
        )

    ### query modifications based on query arguments
    data_query, count_query, start, end = query_add_filter_sort_range_or_400(
        db_model,
        response_model,
        data_query,
        count_query,
        text_fields,
        filter,
        sort,
        range,
    )

    data = data_query.all()
    count = count_query.scalar()

    start, end = fix_start_end(count, start, end)
    response.headers["Content-Range"] = f"{start}-{end}/{count}"
    return data






@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.TeamOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
        424: {"model": ErrorDetail },
    }

)
def invitation_create(
    input: schema.TeamInvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    # check current user is an admin
    team_user_is_admin_or_403(current_user.id, input.team_id, db)

    ## prevent member count more than licenses bought.
    team: Team = db_get_item_or_404(input.team_id, Team, "Team", db)
    if input.is_admin == False and (
        team.number_of_licenses < team_get_member_count(input.team_id, db) + 1
    ):
        print("(573d)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("MEMBER_COUNT_WOULD_BE_MORE_THAN_LICENSE_COUNT_III")
        )

    ## prevent inviting existing user
    existing_user_query = (
        db.query(TeamParticipation, User)
        .join(User, User.id == TeamParticipation.user_id)
        .filter(
            User.email == input.email,
            TeamParticipation.team_id == input.team_id,
            TeamParticipation.is_admin == input.is_admin,
        )
    )
    existing_user = existing_user_query.first()
    if existing_user is not None:
        print("(73d6)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("EMAIL_ALREADY_USER")
        )

    ## add the invitation
    try:
        new_invitation = TeamInvitation(
            email=input.email, 
            team_id=input.team_id, 
            is_admin=input.is_admin,
            inviter_user_id=current_user.id
        )

        db.add(new_invitation)
        db.commit()
        db.refresh(new_invitation)
    except exc.IntegrityError:
        # IntegrityError means that invitation is already in the database.
        # We do not make this a problem because somehow admin may want to
        # resend the email.
        # We rollback to be able to use the session later.
        db.rollback()


    ## send email
    try:
        send_mail_or_424(
            subject = "Saasr | Invitation",
            html_content = html.invite_to_team(
                input.email,
                current_user.name+" "+current_user.surname,
                team.name,
                new_invitation.id
            ),
            sender_email = settings.MAIL_SENDER_EMAIL,
            sender_name = settings.MAIL_SENDER_NAME,
            to_email= input.email,
        )
    except Exception as e:
        print("Exception")
        print(repr(e))
        print(e.with_traceback)

    new_team: Team = db_get_item_or_404(input.team_id, Team, "Team", db)
    return new_team



# Invitation accept or reject-----------------------------------------------------
@router.put(
    "/{invitation_id}",
    response_model=schema.TeamOut,
    responses={
        400: {"model": ErrorDetail },
        401: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    },

    description="Delete invitation and accept or not. If body.is_accept==true, add invitee to participation. Always deletes the invitation. User must be invitee, team admin, or superuser.",
)
def invitation_accept_delete(
    invitation_id: uuid.UUID,
    invitation_response: schema.TeamInvitationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    # assert team exists
    team: Team = db_get_item_or_404(
        invitation_response.team_id, Team, "Team", db
    )

    # assert invitation exists
    invitation: TeamInvitation = db_get_item_or_404(
        invitation_id, TeamInvitation, "Invitation", db
    )

    # assert invitation was for this team
    if invitation_response.team_id != invitation.team_id:
        print("(d6a1)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("INVITATION_NOT_FOR_TEAM")
        )

    # assert current user permissions
    if (
        not current_user.is_superuser
        and not current_user.email == invitation.email
        and not team_user_is_admin(
            current_user.id, invitation_response.team_id, db
        )
    ):
        print("(6a1e)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_NOT_AUTHORIZED_I")
        )

    ## if invitation comes with an accept, add user to team
    if invitation_response.is_accept:
        # assert there is a user in db with this invitation email.
        user_with_email: User = (
            db.query(User).filter(User.email == invitation.email).first()
        )
        if not user_with_email:
            print("(a1e3)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail("INVITEE_NOT_REGISTERED_USER")
            )

        participation_add(
            db,
            schema.TeamParticipationCreate(
                team_id=invitation_response.team_id,
                user_id=user_with_email.id,
                is_admin=invitation.is_admin,
                recurring_payer=False,
            ),
        )

    # delete invitation
    db.delete(invitation)
    db.commit()

    ## return updated team
    db.refresh(team)
    return team
