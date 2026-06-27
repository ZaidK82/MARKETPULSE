from sqlalchemy.orm import Session, joinedload

from app.models.watchlist import WatchlistItem


def get_watchlist_item_by_id(
    db: Session,
    watchlist_item_id: int,
) -> WatchlistItem | None:
    return (
        db.query(WatchlistItem)
        .options(joinedload(WatchlistItem.stock))
        .filter(WatchlistItem.id == watchlist_item_id)
        .first()
    )


def get_watchlist_item_by_stock_id(
    db: Session,
    stock_id: int,
) -> WatchlistItem | None:
    return (
        db.query(WatchlistItem)
        .filter(WatchlistItem.stock_id == stock_id)
        .filter(WatchlistItem.is_active.is_(True))
        .first()
    )


def get_watchlist_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[WatchlistItem]:
    return (
        db.query(WatchlistItem)
        .options(joinedload(WatchlistItem.stock))
        .filter(WatchlistItem.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_watchlist_item(db: Session, stock_id: int) -> WatchlistItem:
    item = WatchlistItem(stock_id=stock_id)

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def deactivate_watchlist_item(
    db: Session,
    watchlist_item: WatchlistItem,
) -> WatchlistItem:
    watchlist_item.is_active = False

    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)

    return watchlist_item