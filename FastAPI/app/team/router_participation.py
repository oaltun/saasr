from typing import Optional, List
from app.core.crud import fix_start_end, query_add_filter_sort_range_or_400
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, TEXT

from app.core.auth import get_current_active_user_or_400
from app.core.schema import ErrorDetail
from app.core.session import get_db

from app.team import schema
from app.team.model import TeamParticipation
from app.user.model import User


participation_router = router = APIRouter(prefix="/team_participations")


@router.get(
    "",
    response_model=List[schema.TeamParticipationOut],
    responses={
        400: {"model": ErrorDetail },
    },
    description="Get all team participations. If current user is super_user, returns all participations. Else returns the team participations of the current user.",
)
def participation_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    

    ### resource setup
    response_model = schema.TeamParticipationOut
    db_model = TeamParticipation
    text_fields = ()  # the fields that will be search with the filter=[q:xxx] query.
    data_query = db.query(db_model)
    count_query = db.query(func.count(db_model.created_at))

    if not current_user.is_superuser:
        data_query = data_query.filter(
            TeamParticipation.user_id == current_user.id
        )
        count_query = count_query.filter(
            TeamParticipation.user_id == current_user.id
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
