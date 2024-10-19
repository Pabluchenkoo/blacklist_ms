from fastapi import APIRouter, HTTPException, status, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

# Create a router for the auth-related endpoints
router = APIRouter()

# Define a request model if any additional data is needed for token generation
class TokenRequest(BaseModel):
    user: str = "test_user"  # Optional user identifier, default is "test_user"

# Endpoint to generate a JWT
@router.post("/", response_model=dict)
def generate_jwt_token(request: TokenRequest, Authorize: AuthJWT = Depends()):
    # Generate a new token using the provided user or a default value
    access_token = Authorize.create_access_token(subject=request.user)
    
    return {"access_token": access_token}