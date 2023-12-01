import json
import uuid
from app.core.auth import get_current_active_superuser_or_403, get_current_active_user_or_400
from app.core.crud import fix_start_end, query_add_filter_sort_range_or_400
from app.core.schema import ErrorDetail
from app.opt.subscription.crud import create_plan
from app.core.error import error_detail
from fastapi import Response, status,  Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.opt.subscription import schema
from typing import List, Optional
from datetime import datetime
from app.opt.subscription.model import Plan

from app.user.model import User
from app.core.session import get_db


plan_router = router = APIRouter(prefix="/subscription_plans")


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schema.Plan
)
def plan_create(
    plan: schema.PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    return create_plan(db, plan)


@router.get("", response_model=List[schema.Plan])
def plan_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
):

    ### resource setup
    response_model = schema.Plan
    db_model = Plan
    text_fields = (  # the fields that will be search with the filter=[q:xxx] query.
        db_model.id,
        db_model.name,
        db_model.description,
        db_model.features,
    )
    data_query = db.query(db_model).order_by(text("created_at asc"))
   
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


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

)
def plan_delete(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    plan_query = db.query(Plan).filter(Plan.id == id)
    plan = plan_query.first()
    if plan == None:
        print("(f8df)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PLAN_DOES_NOT_EXIST")
        )
    plan_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{id}", 
    response_model=schema.Plan,
    responses={
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
    }

    )
def plan_update(
    id: str,
    updated_plan: schema.PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    plan_query = db.query(Plan).filter(Plan.id == id)
    plan = plan_query.first()
    if plan == None:
        print("(8dfa)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PLAN_DOES_NOT_EXIST_II")
        )
    updated_plan.modified_at = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"
    )
    plan_query.update(updated_plan.dict(), synchronize_session=False)
    db.commit()
    return plan_query.first()
