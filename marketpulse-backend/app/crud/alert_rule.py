from sqlalchemy.orm import Session

from app.models.alert_rule import AlertRule
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleUpdate


def get_alert_rule_by_id(db: Session, rule_id: int) -> AlertRule | None:
    return db.query(AlertRule).filter(AlertRule.id == rule_id).first()


def get_alert_rules(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> list[AlertRule]:
    query = db.query(AlertRule)

    if active_only:
        query = query.filter(AlertRule.is_active.is_(True))

    return query.offset(skip).limit(limit).all()


def get_alert_rules_by_stock_id(
    db: Session,
    stock_id: int,
    active_only: bool = True,
) -> list[AlertRule]:
    query = db.query(AlertRule).filter(AlertRule.stock_id == stock_id)

    if active_only:
        query = query.filter(AlertRule.is_active.is_(True))

    return query.all()


def create_alert_rule(
    db: Session,
    alert_rule_data: AlertRuleCreate,
) -> AlertRule:
    alert_rule = AlertRule(
        stock_id=alert_rule_data.stock_id,
        name=alert_rule_data.name.strip(),
        indicator=alert_rule_data.indicator,
        operator=alert_rule_data.operator,
        target_value=alert_rule_data.target_value,
        direction=alert_rule_data.direction,
        timeframe=alert_rule_data.timeframe,
    )

    db.add(alert_rule)
    db.commit()
    db.refresh(alert_rule)

    return alert_rule


def update_alert_rule(
    db: Session,
    alert_rule: AlertRule,
    alert_rule_data: AlertRuleUpdate,
) -> AlertRule:
    update_data = alert_rule_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        update_data["name"] = update_data["name"].strip()

    for field, value in update_data.items():
        setattr(alert_rule, field, value)

    db.add(alert_rule)
    db.commit()
    db.refresh(alert_rule)

    return alert_rule


def deactivate_alert_rule(
    db: Session,
    alert_rule: AlertRule,
) -> AlertRule:
    alert_rule.is_active = False

    db.add(alert_rule)
    db.commit()
    db.refresh(alert_rule)

    return alert_rule