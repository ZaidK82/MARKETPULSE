from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.alert_rule import (
    create_alert_rule,
    deactivate_alert_rule,
    get_alert_rule_by_id,
    get_alert_rules,
    update_alert_rule,
)
from app.crud.stock import get_stock_by_id
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleRead, AlertRuleUpdate


router = APIRouter(
    prefix="/alert-rules",
    tags=["Alert Rules"],
)


@router.post(
    "",
    response_model=AlertRuleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_alert_rule_endpoint(
    alert_rule_data: AlertRuleCreate,
    db: Session = Depends(get_db),
):
    stock = get_stock_by_id(db, alert_rule_data.stock_id)

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found.",
        )

    return create_alert_rule(db, alert_rule_data)


@router.get(
    "",
    response_model=list[AlertRuleRead],
)
def list_alert_rules_endpoint(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    return get_alert_rules(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get(
    "/{rule_id}",
    response_model=AlertRuleRead,
)
def get_alert_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
):
    alert_rule = get_alert_rule_by_id(db, rule_id)

    if not alert_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found.",
        )

    return alert_rule


@router.patch(
    "/{rule_id}",
    response_model=AlertRuleRead,
)
def update_alert_rule_endpoint(
    rule_id: int,
    alert_rule_data: AlertRuleUpdate,
    db: Session = Depends(get_db),
):
    alert_rule = get_alert_rule_by_id(db, rule_id)

    if not alert_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found.",
        )

    return update_alert_rule(
        db=db,
        alert_rule=alert_rule,
        alert_rule_data=alert_rule_data,
    )


@router.delete(
    "/{rule_id}",
    response_model=AlertRuleRead,
)
def delete_alert_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
):
    alert_rule = get_alert_rule_by_id(db, rule_id)

    if not alert_rule or not alert_rule.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found.",
        )

    return deactivate_alert_rule(db=db, alert_rule=alert_rule)