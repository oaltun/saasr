from app.core import security

# Monkey patch function we can use to shave a second off our tests by skipping the password hashing check
def verify_password_mock(first: str, second: str):
    return True


def test_login(client, test_user, monkeypatch):
    # Patch the test to skip password hashing check for speed
    monkeypatch.setattr(security, "verify_password", verify_password_mock)

    response = client.post(
        "/api/token",
        data={"username": test_user.email, "password": "nottheactualpass"},
    )
    assert response.status_code == 200


def test_signup(client, monkeypatch):
    def get_password_hash_mock(first: str, second: str):
        return True

    monkeypatch.setattr(security, "get_password_hash", get_password_hash_mock)

    response = client.post(
        "/api/signup",
        data={"username": "some@email.com", "password": "Random12.#password"},
    )
    assert response.status_code == 200


def test_resignup(client, test_user, monkeypatch):
    # Patch the test to skip password hashing check for speed
    monkeypatch.setattr(security, "verify_password", verify_password_mock)

    response = client.post(
        "/api/signup",
        data={
            "username": test_user.email,
            "password": "Password_hashing_is_skipped_via_monkey_patch11",
        },
    )
    assert response.status_code == 409


def test_wrong_password(client, test_db, test_user, test_password, monkeypatch):
    def verify_password_failed_mock(first: str, second: str):
        return False

    monkeypatch.setattr(
        security, "verify_password", verify_password_failed_mock
    )

    response = client.post(
        "/api/token", data={"username": test_user.email, "password": "wrong"}
    )
    assert response.status_code == 401


def test_wrong_login(client, test_db, test_user, test_password):
    response = client.post(
        "/api/token",
        data={"username": "fakeuser@gmail.com", "password": test_password},
    )
    assert response.status_code == 401
