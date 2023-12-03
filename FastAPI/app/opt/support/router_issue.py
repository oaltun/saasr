from typing import Optional, List
import uuid
from app.core.auth import get_current_active_user_or_400
from app.core.crud import fix_start_end, query_add_filter_sort_range_or_400
from app.core.schema import ErrorDetail
from app.core.session import get_db
from app.core.error import error_detail
from fastapi import APIRouter, Depends,  status, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, TEXT
from app.opt.support import schema

from app.opt.support.model import Issue, Message
from app.user.model import User


issue_router = router = APIRouter(prefix="/support_issues")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.IssueOut,
    description="Create one issue and its first message",
)
def issue_create(
    input: schema.IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    # first add the issue
    new_issue = Issue(
        owner_id=current_user.id, title=input.title, is_closed=False
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    # then add its message
    new_message = Message(
        issue_id=new_issue.id, owner_id=current_user.id, text=input.message_text
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_issue


# get all -----------------------------------------------
@router.get("", response_model=List[schema.IssueOutInList])
def issue_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    ### resource setup
    response_model = schema.IssueOutInList
    db_model = Issue
    text_fields = (  # the fields that will be search with the filter=[q:xxx] query.
        cast(db_model.id, TEXT),
        db_model.title,
    )
    data_query = db.query(db_model)
    count_query = db.query(func.count(db_model.id))

    if not current_user.is_superuser:
        data_query = data_query.filter(Issue.owner_id == current_user.id)
        count_query = count_query.filter(Issue.owner_id == current_user.id)

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



@router.get(
    "/{id}",
    response_model=schema.IssueOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    },
    description="get one issue and its messages",
)
def issue_get(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    issue = db.query(Issue).filter(Issue.id == id).first()

    if not issue:
        print("(dfa7)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("ISSUE_DOES_NOT_EXIST")
        )

    if issue.owner_id != current_user.id:
        print("(bc85)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("USER_NOT_ISSUE_OWNER")
        )

    return issue




@router.put(
    "/{id}", 
    response_model=schema.IssueOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

)
def issue_status_close(
    id: uuid.UUID,
    status_update: schema.IssueStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    if status_update.is_closed != True:
        print("(4a97)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("ATTEMPT_TO_OPEN_ISSUE")
        )

    ## check if such issue exists
    issue_query = db.query(Issue).filter(Issue.id == id)
    issue = issue_query.first()

    if issue == None:
        print("(a616)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("ATTEMPT_TO_OPEN_ISSUE")
        )

    if issue.is_closed:
        print("fdf1")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("ISSUE_ALREADY_CLOSED")
        )

    ## check the authorization
    if not issue.owner_id == current_user.id and not current_user.is_superuser:
        print("df1c")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("NOT_AUTHORIZED_TO_CLOSE_THE_ISSUE")
        )


    ## close the issue if it is open. We do not open a closed issue for the time being.
    if (status_update.is_closed == True) and (issue.is_closed != status_update.is_closed):
        issue_query.update(
            {
                "is_closed": status_update.is_closed,
                "closer_id": current_user.id,
                "closed_at": func.now()
            }, 
            synchronize_session=False
        )
        db.commit()
        return issue_query.first()
    else:
        return issue
