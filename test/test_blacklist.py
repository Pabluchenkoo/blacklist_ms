import pytest
from unittest.mock import AsyncMock
from main import app
from app.database import get_db
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

# Fixture para el cliente asíncrono
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# Fixture para mockear AuthJWT
@pytest.fixture
def mock_authjwt():
    class MockAuthJWT:
        def jwt_required(self):
            pass  # Simula un JWT válido
        def get_jwt_subject(self):
            return "127.0.0.1"  # IP simulada
    return MockAuthJWT()

# Fixture para mockear la sesión de la base de datos
@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

# Fixture para sobreescribir las dependencias
@pytest.fixture(autouse=True)
def override_dependencies(mock_authjwt, mock_db):
    # Sobrescribir la dependencia AuthJWT
    def override_authjwt():
        return mock_authjwt
    # Sobrescribir la dependencia get_db
    async def override_get_db():
        yield mock_db
    app.dependency_overrides[AuthJWT] = override_authjwt
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides = {}

# Prueba para agregar un correo a la lista negra cuando no existe previamente
@pytest.mark.asyncio
async def test_add_to_blacklist(mock_db, async_client):
    blacklist_data = {
        "email": "test@example.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Spam"
    }

    # Configurar el mock para que simule que el correo no está en la lista negra
    async def mock_execute(*args, **kwargs):
        class Result:
            def scalars(self):
                class Scalars:
                    def first(self):
                        return None  # Simula que el correo no existe
                return Scalars()
        return Result()
    mock_db.execute.side_effect = mock_execute
    mock_db.commit = AsyncMock()

    response = await async_client.post("/blacklists/", json=blacklist_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Email added to the blacklist successfully."}

# Prueba para intentar agregar un correo que ya existe
@pytest.mark.asyncio
async def test_add_to_blacklist_existing_email(mock_db, async_client):
    blacklist_data = {
        "email": "existing@example.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Spam"
    }

    # Configurar el mock para que simule que el correo ya está en la lista negra
    async def mock_execute(*args, **kwargs):
        class Result:
            def scalars(self):
                class Scalars:
                    def first(self):
                        from app.models.blacklist import Blacklist
                        return Blacklist(email="existing@example.com")
                return Scalars()
        return Result()
    mock_db.execute.side_effect = mock_execute

    response = await async_client.post("/blacklists/", json=blacklist_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email is already blacklisted"}

# Prueba para verificar un correo en la lista negra (cuando está en la lista)
@pytest.mark.asyncio
async def test_check_blacklist_blacklisted(mock_db, async_client):
    email = "blacklisted@example.com"

    # Configurar el mock para que simule que el correo está en la lista negra
    async def mock_execute(*args, **kwargs):
        class Result:
            def scalars(self):
                class Scalars:
                    def first(self):
                        from app.models.blacklist import Blacklist
                        return Blacklist(email=email, blocked_reason="Spam")
                return Scalars()
        return Result()
    mock_db.execute.side_effect = mock_execute

    response = await async_client.get(f"/blacklists/{email}")
    assert response.status_code == 200
    assert response.json() == {"blacklisted": True, "blocked_reason": "Spam"}

# Prueba para verificar un correo en la lista negra (cuando no está en la lista)
@pytest.mark.asyncio
async def test_check_blacklist_not_blacklisted(mock_db, async_client):
    email = "not_blacklisted@example.com"

    # Configurar el mock para que simule que el correo no está en la lista negra
    async def mock_execute(*args, **kwargs):
        class Result:
            def scalars(self):
                class Scalars:
                    def first(self):
                        return None  # Simula que el correo no existe
                return Scalars()
        return Result()
    mock_db.execute.side_effect = mock_execute

    response = await async_client.get(f"/blacklists/{email}")
    assert response.status_code == 200
    assert response.json() == {"blacklisted": False, "blocked_reason": None}
