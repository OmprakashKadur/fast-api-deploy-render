from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.utils import create_access_token, generate_password_hash, verify_password
from src.db import get_session
from src.models import User
from src.schemas import TokenResponse, UserCreate, UserLogin, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user account with hashed password."""
    # Check if user with same email exists
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    new_user = User(
        email=user_data.email,
        password=generate_password_hash(user_data.password),
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain access token",
)
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Verify credentials and return a JWT access token."""
    query = select(User).where(User.email == login_data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@auth_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current logged-in user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated user's profile."""
    return current_user
