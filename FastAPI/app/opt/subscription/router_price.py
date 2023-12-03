from app.core.crud import fix_start_end, query_add_filter_sort_range_or_400
from app.opt.subscription.schema import PriceOut
from fastapi import Depends, APIRouter, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.opt.subscription.model import Price
from app.core.session import get_db


price_router = router = APIRouter(prefix="/subscription_prices")


@router.get("", response_model=List[PriceOut])
def price_list(
    response: Response,
    filter: Optional[str] = None,
    sort: Optional[str] = None,
    range: Optional[str] = None,
    db: Session = Depends(get_db),
):

    ### resource setup
    response_model = PriceOut
    db_model = Price
    text_fields = (  # the fields that will be search with the filter=[q:xxx] query.
        db_model.plan_id,
        db_model.billing_cycle_id,
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
