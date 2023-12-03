import uuid
from app.core.auth import get_current_active_superuser_or_403, get_current_active_user_or_400
from app.core.crud import fix_start_end, query_add_filter_sort_range_or_400
from fastapi import Response, status,  Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.core.schema import ErrorDetail

from app.opt.subscription.model import BillingCycle
from app.user.model import User
from app.opt.subscription import schema
from typing import List, Optional
from datetime import datetime
from app.core.session import get_db
from sqlalchemy import func, cast, TEXT, text


billing_cycle_router = router = APIRouter(prefix="/subscription_billing_cycles")


@router.post(
    "", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schema.BillingCycle,
    responses={
        403: {"model": ErrorDetail },
    }
)
def billing_cycle_create(
    billing_cycle: schema.BillingCycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    new_billing_cycle = BillingCycle(**billing_cycle.dict())
    db.add(new_billing_cycle)
    db.commit()
    db.refresh(new_billing_cycle)

    return new_billing_cycle



@router.get("", response_model=List[schema.BillingCycle])
def billing_cycle_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
):
    ### resource setup
    response_model = schema.BillingCycle
    db_model = BillingCycle
    text_fields = (  # the fields that will be search with the filter=[q:xxx] query.
        db_model.id,
        db_model.name,
        db_model.description,
    )
    data_query = db.query(db_model).order_by(text("billing_period_in_months asc"))
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
def billing_cycle_delete(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    billing_cycle_query = db.query(BillingCycle).filter(BillingCycle.id == id)
    billing_cycle = billing_cycle_query.first()
    if billing_cycle == None:
        print("(01f8)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_DOES_NOT_EXIST")
        )
    billing_cycle_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schema.BillingCycle)
def billing_cycle_update(
    id: str,
    updated_billing_cycle: schema.BillingCycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):

    billing_cycle_query = db.query(BillingCycle).filter(BillingCycle.id == id)
    billing_cycle = billing_cycle_query.first()
    if billing_cycle == None:
        print("1f8d")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_DOES_NOT_EXIST_II")
        )
    updated_billing_cycle.modified_at = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"
    )
    billing_cycle_query.update(
        updated_billing_cycle.dict(), synchronize_session=False
    )
    db.commit()
    return billing_cycle_query.first()
