from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.blacklist import Blacklist
from app.schemas.blacklist_schema import BlacklistCreate, BlacklistResponse
from app.database import get_db
from fastapi_jwt_auth import AuthJWT

router = APIRouter()

# Health Check Route
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"} 

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_blacklist(
    blacklist_data: BlacklistCreate,
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    request_ip = Authorize.get_jwt_subject()

    result = await db.execute(select(Blacklist).filter_by(email=blacklist_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already blacklisted"
        )

    new_entry = Blacklist(
        email=blacklist_data.email,
        app_uuid=str(blacklist_data.app_uuid),
        blocked_reason=blacklist_data.blocked_reason,
        request_ip=request_ip
    )
    #db.add(new_entry)
    await db.commit()

    return {"message": "Email added to the blacklist successfully."}

@router.get("/{email}", response_model=dict, status_code=status.HTTP_200_OK)
async def check_blacklist(
    email: str,
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    
    result = await db.execute(select(Blacklist).filter_by(email=email))
    entry = result.scalars().first()

    if entry:
        return {
            "blacklisted": True,
            "blocked_reason": entry.blocked_reason
        }

    return {
        "blacklisted": False,
        "blocked_reason": None
    }
