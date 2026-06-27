from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.schemas.stock import StockCreate


def get_stock_by_id(db: Session, stock_id: int) -> Stock | None:
    return db.query(Stock).filter(Stock.id == stock_id).first()


def get_stock_by_symbol(db: Session, symbol: str) -> Stock | None:
    normalized_symbol = symbol.upper().strip()
    return db.query(Stock).filter(Stock.symbol == normalized_symbol).first()


def get_stocks(db: Session, skip: int = 0, limit: int = 100) -> list[Stock]:
    return db.query(Stock).offset(skip).limit(limit).all()


def create_stock(db: Session, stock_data: StockCreate) -> Stock:
    stock = Stock(
        symbol=stock_data.symbol.upper().strip(),
        name=stock_data.name,
        exchange=stock_data.exchange,
        currency=stock_data.currency,
    )

    db.add(stock)
    db.commit()
    db.refresh(stock)

    return stock