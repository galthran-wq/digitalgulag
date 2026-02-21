import uuid
from datetime import datetime, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.auth import create_token_for_user
from src.core.config import settings
from src.core.database import Base, get_postgres_session
from src.main import app
from src.models.postgres.users import UserModel


engine = create_async_engine(settings.postgres_url, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_postgres_session] = override_get_session
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="fake",
        is_verified=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: UserModel) -> dict[str, str]:
    token = create_token_for_user(test_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def authed_client(client: httpx.AsyncClient, auth_headers: dict[str, str]):
    client.headers.update(auth_headers)
    yield client
