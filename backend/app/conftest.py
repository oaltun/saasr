import os
import requests
from app.initial_data import init_all
from app.team.schema import TeamOut
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from fastapi.testclient import TestClient
import typing as t


from app.core import security
from app.config import settings
from app.core.session import Base, get_db
from app.user import model
from app.main import app

import os


# this is used in mail sending functions
os.environ["IS_TESTING"] = "true"


def get_test_db_url() -> str:
    # return f"{config.SQLALCHEMY_DATABASE_URI}_test"
    return f"{settings.DATABASE_URL}_test"


@pytest.fixture
def test_db():
    """
    Modify the db session to automatically roll back after each test.
    This is to avoid tests affecting the database state of other tests.
    """
    # Connect to the test database
    engine = create_engine(
        get_test_db_url(),
    )

    connection = engine.connect()
    trans = connection.begin()

    # Run a parent transaction that can roll back all changes
    test_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    test_session = test_session_maker()
    test_session.begin_nested()

    @event.listens_for(test_session, "after_transaction_end")
    def restart_savepoint(s, transaction):
        if transaction.nested and not transaction._parent.nested:
            s.expire_all()
            s.begin_nested()

    yield test_session

    # Roll back the parent transaction after the test is complete
    test_session.close()
    trans.rollback()
    connection.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Create a test database and use it for the whole test session.
    """

    test_db_url = get_test_db_url()
    if database_exists(test_db_url):
        test_engine = create_engine(test_db_url)
        drop_database(test_db_url)

    create_database(test_db_url)
    test_engine = create_engine(test_db_url)
    Base.metadata.create_all(test_engine)

    # Run the tests
    yield

    # Drop the test database
    drop_database(test_db_url)


@pytest.fixture
def client(test_db):
    """
    Get a TestClient instance that reads/write to the test database.
    """

    def get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = get_test_db

    yield TestClient(app)


@pytest.fixture
def test_password() -> str:
    return "securepassword"


def get_password_hash() -> str:
    """
    Password hashing can be expensive so a mock will be much faster
    """
    return "supersecrethash"


@pytest.fixture
def test_user(test_db) -> model.User:
    """
    Make a test user in the database
    """

    user = model.User(
        email="fake@email.com",
        name="Fake",
        surname="Faker",
        hashed_password=get_password_hash(),
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def test_user2(test_db) -> model.User:
    """
    Make a test user in the database
    """

    user = model.User(
        email="fake2@email.com",
        name="Fake Two Faker",
        surname="Fake Two Faker",
        hashed_password=get_password_hash(),
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def test_superuser(test_db) -> model.User:
    """
    Superuser for testing
    """

    user = model.User(
        email="fakeadmin@email.com",
        name="Fake Admin",
        surname="Fake Admin",
        hashed_password=get_password_hash(),
        is_active=True,
        is_superuser=True,
    )
    test_db.add(user)
    test_db.commit()
    return user


def verify_password_mock(first: str, second: str) -> bool:
    return True


@pytest.fixture
def user_token_headers(
    client: TestClient, test_user, test_password, monkeypatch
) -> t.Dict[str, str]:
    monkeypatch.setattr(security, "verify_password", verify_password_mock)

    login_data = {
        "username": test_user.email,
        "password": test_password,
    }
    r = client.post("/api/token", data=login_data)

    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def user2_token_headers(
    client: TestClient, test_user2, test_password, monkeypatch
) -> t.Dict[str, str]:
    monkeypatch.setattr(security, "verify_password", verify_password_mock)

    login_data = {
        "username": test_user2.email,
        "password": test_password,
    }
    r = client.post("/api/token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def superuser_token_headers(
    client: TestClient, test_superuser, test_password, monkeypatch
) -> t.Dict[str, str]:
    monkeypatch.setattr(security, "verify_password", verify_password_mock)

    login_data = {
        "username": test_superuser.email,
        "password": test_password,
    }
    r = client.post("/api/token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


### product ---------------------------
@pytest.fixture
def product_info(test_db):
    init_all(test_db)


## initial data
@pytest.fixture
def initial_data(test_db):
    init_all(test_db)


### team -------------------------
@pytest.fixture
def test_team(
    client: TestClient,
    product_info,
    test_user: model.User,
    user_token_headers,
    test_user2: model.User,
    user2_token_headers,
):
    ### create the team
    team_data: t.Dict[str, str] = {
        # "recurring_billing_is_on": True,
        # "name": "user 0 team",
    }
    response = client.post("/api/v1/teams", json=team_data, headers=user_token_headers)

    team: TeamOut = TeamOut(**response.json())

    assert response.status_code == 201
    # assert team.participations[0].user_id == test_user.id
    # assert team.participations[0].is_admin == True
    # assert team.recurring_billing_is_on == team_data["recurring_billing_is_on"]

    # ### invite test_user0 as an admin
    # fm.config.SUPPRESS_SEND = 1
    # invitation_data = {
    #     "team_id": str(team.id),
    #     "email": test_user0["email"],
    #     "is_admin": True,
    # }
    # response = authorized_client1.post(
    #     "/teams/invitation", json=invitation_data
    # )
    # team = TeamOut(**response.json())
    # assert team.name == team_data["name"]
    # assert team.team_invitations[0].email == test_user0["email"]

    # ### let test_user0 accept admin invitation
    # response = authorized_client0.put(
    #     f"/teams/invitation/{team.team_invitations[0].id}",
    #     json={"team_id": str(team.id), "is_accept": True},
    # )
    # team = TeamOut(**response.json())
    # assert len(team.team_invitations) == 0  # invitation must be deleted
    # assert test_user0["id"] in [
    #     participation.user_id for participation in team.team_participations
    # ]

    return team
