import uuid
from app.config import settings
from app.user.crud import create_user
from app.user.schema import UserCreate


super_user = dict(
    email=settings.SAASR_SUPERUSER_EMAIL,
    password=settings.SAASR_SUPERUSER_PASSWORD,
    is_active=True,
    is_superuser=True,
    is_verified=True,
)


def init_superuser(db):
    return create_user(
        db,
        UserCreate(**super_user),
    )

def init_fake_users(db, count=20):
    print("Creating fake users")
    for i in range(0, count):
        print(
            ".",
        )
        user_data = dict(
            email="fake_" + str(i) + "_" + str(uuid.uuid4()) + "@example.com",
            password="fake_" + str(i) + str(uuid.uuid4()),
            is_active=True,
            is_verified=True,
            is_superuser=False,
        )
        create_user(
            db,
            UserCreate(**user_data),
        )