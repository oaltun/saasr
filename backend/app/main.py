import uvicorn
from pydantic import BaseConfig

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from app.config import settings
from app.core.session import SessionLocal
from app.core.auth import get_current_active_user_or_400
from app.user.router_users import users_router
from app.user.router_auth import auth_router
from app.team.router_team import team_router
from app.team.router_participation import participation_router
from app.team.router_invitation import invitation_router


# ========== #
# UNIQUE ID
# ========== #


def custom_generate_unique_id(route: APIRoute) -> str:
    """Automatic client generators generate functions based on this"""
    r = f"{route.tags[0]}_{route.name}"
    return r


# ========== #
# API PREFIX
# ========== #

prefix = "/api/v1"

# ========== #
# API VERSION
# ========== #

version = "0.01"

# ========== #
# FASTAPI APP
# ========== #

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=version,
    docs_url="/api/docs",
    openapi_url="/api",
    generate_unique_id_function=custom_generate_unique_id,
)
BaseConfig.arbitrary_types_allowed = True  # change #1


# ========== #
# ERROR INTERCEPTORS
# ========== #


# Intercept when there is a validation error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, e):
    print(f"Request validation error! Request: {repr(request)} Error:{repr(e)}")
    return await request_validation_exception_handler(request, e)


# Intercept when returning an HTTPException
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e: HTTPException):
    print(f"HTTP error! Request: {repr(request)} Error: {repr(e)}")
    # Convert to JSONResponse. Automatic client generators can pick up this type.
    h = JSONResponse(status_code=e.status_code, content=e.detail, headers=e.headers)
    print("JSONResponse:" + repr(h))
    return h


# ========== #
# CORS SETTINGS
# ========== #

allow_origins = [
    "https://saasr.example.com",
    "https://example.com",
    "https://www.example.com",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ========== #
# HTTP MIDDLEWARE
# ========== #


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


# ========== #
# ROUTERS
# ========== #


@app.get(f"{prefix}/hello", tags=["hello"])
async def hello():
    return {"message": f"Hello World!"}


app.include_router(auth_router, prefix="/api", tags=["auth"])

app.include_router(
    users_router,
    prefix=prefix,
    tags=["users"],
    dependencies=[Depends(get_current_active_user_or_400)],
)

app.include_router(
    team_router,
    prefix=prefix,
    tags=["teams"],
    dependencies=[Depends(get_current_active_user_or_400)],
)

app.include_router(
    invitation_router,
    prefix=prefix,
    tags=["teams"],
    dependencies=[Depends(get_current_active_user_or_400)],
)

app.include_router(
    participation_router,
    prefix=prefix,
    tags=["teams"],
    dependencies=[Depends(get_current_active_user_or_400)],
)

# ========== #
# OPTIONAL FEAT ROUTERS
# ========== #

try:
    from app.opt.support.router_issue import issue_router
    from app.opt.support.router_message import message_router

    app.include_router(
        issue_router,
        prefix=prefix,
        tags=["support"],
        dependencies=[Depends(get_current_active_user_or_400)],
    )
    app.include_router(
        message_router,
        prefix=prefix,
        tags=["support"],
        dependencies=[Depends(get_current_active_user_or_400)],
    )
except:
    pass


try:
    from app.opt.subscription.router_period import billing_cycle_router
    from app.opt.subscription.router_plan import plan_router
    from app.opt.subscription.router_price import price_router

    app.include_router(
        billing_cycle_router,
        prefix=prefix,
        tags=["subscription"],
    )
    app.include_router(
        plan_router,
        prefix=prefix,
        tags=["subscription"],
    )
    app.include_router(
        price_router,
        prefix=prefix,
        tags=["subscription"],
    )
except:
    pass


try:
    from app.opt.payment.router_iyzico import payment_router
    from app.opt.payment.router_card import card_router

    app.include_router(
        payment_router,
        prefix=prefix,
        tags=["payment"],
        dependencies=[Depends(get_current_active_user_or_400)],
    )

    app.include_router(
        card_router,
        prefix=prefix,
        tags=["payment"],
        dependencies=[Depends(get_current_active_user_or_400)],
    )
except:
    pass

# ========== #
# MAIN
# ========== #

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", reload=True, port=8888)
