import json
from sqlalchemy import func, cast, TEXT
from sqlalchemy.orm import Session
import uuid
from app.core import session
from app.core.crud import (
    fix_start_end,
    query_add_filter_sort_range_or_400,
)
from app.core.schema import ErrorDetail
from app.team.model import TeamInvitation, TeamParticipation
from app.team.util import get_user_lastest_term_end
from fastapi import APIRouter, Request, Depends, Response, HTTPException

from typing import Optional, Dict, List

from app.core.session import get_db
from app.user.crud import (
    get_user_or_404,
    create_user,
    delete_user_or_404,
    edit_user_or_404,
)
from app.user.schema import (
    UserCreate,
    UserEdit,
    User,
    UserSubscriptionInfo,
)
from app.core.auth import get_current_active_user_or_400, get_current_active_superuser_or_403
from app.user.model import User as UserModel


users_router = r = APIRouter()


@r.get(
    "/users",
    response_model=List[User],
    response_model_exclude_none=True,
    responses={
        403: {"model": ErrorDetail },
    }

)
async def user_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser_or_403),
):
    """
    Get all users
    """

    ### resource setup
    response_model = User
    db_model = UserModel
    text_fields = (  # the fields that will be search with the filter=[q:xxx] query.
        cast(db_model.id, TEXT),
        db_model.email,
        db_model.name,
        db_model.surname,
    )
    data_query = db.query(db_model)
    count_query = db.query(func.count(db_model.id))

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






@r.get(
    "/users/me", 
    response_model=User, 
    response_model_exclude_none=True,
    responses={
        400: {"model": ErrorDetail },
    }
)
async def user_me(current_user=Depends(get_current_active_user_or_400)):
    """
    Get own user
    """
    return current_user






@r.get(
    "/users/subscription_info",
    response_model=UserSubscriptionInfo,
    response_model_exclude_none=True,
)
async def user_subscription_info_get(
    current_user=Depends(get_current_active_user_or_400), db=Depends(get_db)
):
    """
    Get own user
    """
    invitation_count = (
        db.query(TeamInvitation)
        .filter(TeamInvitation.email == current_user.email)
        .scalar()
    ) or 0
    participation_count = (
        db.query(TeamParticipation)
        .filter(TeamParticipation.user_id == current_user.id)
        .scalar()
    ) or 0

    if participation_count == 0:
        term_end = 0
    else:
        term_end = get_user_lastest_term_end(current_user.id, db)

    return UserSubscriptionInfo(
        invitation_count=invitation_count,
        participation_count=participation_count,
        term_end=term_end,
    )




@r.get(
    "/users/{user_id}",
    response_model=User,
    response_model_exclude_none=True,
    responses={
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }
)
async def user_get(
    request: Request,
    user_id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser_or_403),
):
    """
    Get any user details
    """
    user = get_user_or_404(db, user_id)
    return user







@r.post(
    "/users", 
    response_model=User, 
    response_model_exclude_none=True,
    responses={
        403: {"model": ErrorDetail },
    }
)
async def user_create(
    request: Request,
    user: UserCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser_or_403),
):
    """
    Create a new user
    """
    return create_user(db, user)




@r.put(
    "/users/{user_id}", 
    response_model=User, 
    response_model_exclude_none=True,
    responses={
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

)
async def user_update(
    request: Request,
    user_id: uuid.UUID,
    user: UserEdit,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser_or_403),
):
    """
    Update existing user
    """
    return edit_user_or_404(db, user_id, user)




@r.delete(
    "/users/{user_id}", 
    response_model=User, 
    response_model_exclude_none=True,
    responses={
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }
)
async def user_delete(
    request: Request,
    user_id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser_or_403),
):
    """
    Delete existing user
    """
 
    return delete_user_or_404(db, user_id)
