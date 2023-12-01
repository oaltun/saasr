import json
from sqlalchemy import text, or_
import typing as t
from app.config import settings
from app.core.error import error_detail
from fastapi import status, HTTPException

# def raise HTTPException(status_code, detail, headers):
#     raise HTTPException(
#         status_code=status_code,
#         detail=detail,
#         headers={"X-Error": detail}
#     )

def raise_if(condition, status_code, error_code):
    if condition:
        raise HTTPException(
            status_code=status_code,
            detail=error_detail(error_code)
        )




def fix_start_end(count, start, end):
    if count == 0:
        start = 0
        end = 0
    else:
        if start is None:
            start = 1
        if end is None:
            end = count
    return start, end


def add_search(query, search, text_fields):
    if search and len(text_fields) != 0:
        query = query.filter(
            or_(field.like("%" + search + "%") for field in text_fields)
        )
    return query


def add_order_by(query, order_by, asc):
    if order_by:
        if asc:
            dirn = "asc"
        else:
            dirn = "desc"
        query = query.order_by(text(order_by + " " + dirn))
    return query


def add_limit_offset(query, limit, offset):
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    return query


def query_add_filter_sort_range_or_400(
    db_model,
    response_model,
    data_query,
    count_query,
    text_fields,
    filter,
    sort,
    range,
):
    ### filtering etc
    
    if filter:
        filter: t.Dict = json.loads(filter)
        search = filter.pop("q", None)
        data_query = add_search(data_query, search, text_fields)
        count_query = add_search(count_query, search, text_fields)

    if sort:
        sort_column, direction = json.loads(sort)
        order_by = None
        if sort_column in response_model.__fields__:
            order_by = sort_column
        asc = True
        if direction.lower() == "desc":
            asc = False
        data_query = add_order_by(data_query, order_by, asc)

    start = None
    end = None
    if range:
        # limiting
        # the parameters start and end start counting from zero.
        start, end = json.loads(range)
        if start > end:
            print("(87d5ac0c)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail("START_IS_LARGER_THAN_END")
            )
        if start < 0:
            print("(dd61422d)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail("START_IS_LESS_THAN_ZERO")
            )

        # [0-9]: skip=0, limit=10: end-start+1
        # [10-19]: skip=10, limit=10

        skip = start
        limit = end - start + 1
        data_query = add_limit_offset(data_query, limit, skip)

    return data_query, count_query, start, end
