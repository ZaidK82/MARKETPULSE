from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.stock import (
    create_stock,
    get_stock_by_id,
    get_stock_by_symbol,
    get_stocks,
)
from app.schemas.stock import StockCreate, StockRead


router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


@router.post(
    "",
    response_model=StockRead,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_endpoint(
    stock_data: StockCreate,
    db: Session = Depends(get_db),
):
    existing_stock = get_stock_by_symbol(db, stock_data.symbol)

    if existing_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock with this symbol already exists.",
        )

    return create_stock(db, stock_data)


@router.get(
    "",
    response_model=list[StockRead],
)
def list_stocks_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_stocks(db, skip=skip, limit=limit)


@router.get(
    "/{stock_id}",
    response_model=StockRead,
)
def get_stock_endpoint(
    stock_id: int,
    db: Session = Depends(get_db),
):
    stock = get_stock_by_id(db, stock_id)

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found.",
        )

    return stock