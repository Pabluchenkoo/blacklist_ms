from fastapi import FastAPI
from pydantic import BaseSettings
from app.models import Blacklist
from app.routes.blacklist_route import router as blacklist_router
from app.routes.jwt_routes import router as jwt_router
from app.database import engine
from app.database import Base
from fastapi_jwt_auth import AuthJWT
from config import settings
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str = settings.JWT_SECRET_KEY

@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    generate_static_jwt()

app.include_router(blacklist_router, prefix="/blacklists")
app.include_router(jwt_router, prefix="/token")

def generate_static_jwt():
    Authorize = AuthJWT()
    
    subject = "test_user"  
    
    access_token = Authorize.create_access_token(subject=subject, expires_time=3600)  

    logging.info(f"Static JWT for testing: {access_token}")