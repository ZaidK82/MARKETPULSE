from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.stock import get_stock_by_id
from app.crud.watchlist import (
    create_watchlist_item,
    deactivate_watchlist_item,
    get_watchlist_item_by_id,
    get_watchlist_item_by_stock_id,
    get_watchlist_items,
)
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemRead


router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)


@router.post(
    "",
    response_model=WatchlistItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_watchlist_item_endpoint(
    watchlist_data: WatchlistItemCreate,
    db: Session = Depends(get_db),
):
    stock = get_stock_by_id(db, watchlist_data.stock_id)

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found.",
        )

    existing_item = get_watchlist_item_by_stock_id(db, watchlist_data.stock_id)

    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock is already in active watchlist.",
        )

    return create_watchlist_item(db, watchlist_data.stock_id)


@router.get(
    "",
    response_model=list[WatchlistItemRead],
)
def list_watchlist_items_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_watchlist_items(db, skip=skip, limit=limit)


@router.delete(
    "/{watchlist_item_id}",
    response_model=WatchlistItemRead,
)
def delete_watchlist_item_endpoint(
    watchlist_item_id: int,
    db: Session = Depends(get_db),
):
    watchlist_item = get_watchlist_item_by_id(db, watchlist_item_id)

    if not watchlist_item or not watchlist_item.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    return deactivate_watchlist_item(db, watchlist_item)