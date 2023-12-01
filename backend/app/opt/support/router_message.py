from app.core.error import error_detail
from fastapi import APIRouter, Depends,  status, HTTPException
from sqlalchemy.orm import Session
from app.core.schema import ErrorDetail

from app.opt.support import schema
from app.opt.support.model import Issue, Message
from app.user.model import User
from app.core.session import get_db
from app.core.auth import get_current_active_user_or_400


message_router = router = APIRouter(
    prefix="/support_messages",
)


@router.post(
    "", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schema.MessageOut,
    responses={
        400: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

)
def message_create(
    input: schema.MessageCreate,  # title and message
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    ## check that resource exists
    issue: Issue = db.query(Issue).filter(Issue.id == input.issue_id).first()
    if not issue:
        print("(f1c1)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("ISSUE_DOES_NOT_EXIST_III")
        )

    ## check authorization
    if not issue.owner_id == current_user.id and not current_user.is_superuser:
        print("(e191)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("USER_NOT_AUTHORIZED")
        )

    ## check that issue is not closed
    if issue.is_closed:
        print("(1912)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("ISSUE_CLOSED")
        )       

    new_message = Message(owner_id=current_user.id, **input.dict())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message
