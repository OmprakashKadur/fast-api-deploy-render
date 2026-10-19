import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.db import get_session
from src.models import Book, User
from src.schemas import BookCreate, BookResponse, BookUpdate

book_router = APIRouter(prefix="/books", tags=["books"])


@book_router.get(
    "/",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all books",
)
async def get_all_books(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
    session: AsyncSession = Depends(get_session),
):
    """Retrieve all books with optional pagination."""
    query = select(Book).order_by(Book.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    books = result.scalars().all()
    return books


@book_router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
)
async def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new book entry associated with the authenticated user."""
    new_book = Book(
        **book_data.model_dump(),
        user_id=current_user.id,
    )
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book


@book_router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get book by ID",
)
async def get_book_by_id(
    book_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Retrieve a single book by its UUID."""
    query = select(Book).where(Book.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return book


@book_router.patch(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a book",
)
async def update_book(
    book_id: uuid.UUID,
    book_update_data: BookUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update fields of an existing book. Only the author or owner can update."""
    query = select(Book).where(Book.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )

    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this book",
        )

    update_dict = book_update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(book, field, value)

    await session.commit()
    await session.refresh(book)
    return book


@book_router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
)
async def delete_book(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a book entry. Only the owner can delete their book."""
    query = select(Book).where(Book.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )

    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this book",
        )

    await session.delete(book)
    await session.commit()
    return None
