import pytest
import os  # For reading environment variables
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app  # Assuming your FastAPI app is initialized in main.py
from app.models.blacklist import Blacklist  # Assuming your models are in app.database
import uuid  # For generating unique email addresses
import asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def auth_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/token/", json={"user": "test_user"})
        return response.json()["access_token"]

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
async def test_db():
    # Read the database URL from the environment variable
    db_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Blacklist.metadata.create_all)
    # Create session maker
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_generate_jwt_token(async_client):
    # Test the JWT generation endpoint
    response = await async_client.post("/token/", json={"user": "test_user"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_add_to_blacklist(async_client, test_db, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Generate a random email for testing
    random_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    response = await async_client.post("/blacklists/", json={
        "email": random_email,
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Spam"
    }, headers=headers)
    
    response_data = response.json()
    print(response_data)  # Print the response body for debugging
    
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_check_blacklist(async_client, test_db, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Generate a random email for testing
    random_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    # Step 1: Add the email to the blacklist first (ensure it returns 201)
    response = await async_client.post("/blacklists/", json={
        "email": random_email,
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Spam"
    }, headers=headers)
    assert response.status_code == 201, f"Failed to add to blacklist with status {response.status_code}"
    
    # Step 2: Check if the email is blacklisted (should return 200 and confirm it's blacklisted)
    response = await async_client.get(f"/blacklists/{random_email}", headers=headers)
    assert response.status_code == 200, f"Failed with status {response.status_code}"
    response_data = response.json()
    print(response_data)  # Debug print for verification

    assert response_data == {
        "blacklisted": True,
        "blocked_reason": "Spam"
    }, f"Unexpected response data: {response_data}"

    # Step 3: Check an email that does not exist (should return 200 but not blacklisted)
    non_existent_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
    response = await async_client.get(f"/blacklists/{non_existent_email}", headers=headers)
    assert response.status_code == 200, f"Failed with status {response.status_code}"
    response_data = response.json()
    print(response_data)  # Debug print for verification

    assert response_data == {
        "blacklisted": False,
        "blocked_reason": None
    }, f"Unexpected response data: {response_data}"
