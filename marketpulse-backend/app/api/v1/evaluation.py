from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.alert_rule import get_alert_rule_by_id
from app.crud.stock import get_stock_by_id
from app.schemas.evaluation import EvaluationResultRead
from app.services.evaluation_service import AlertEvaluationError, evaluate_alert_rule


router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)


@router.post(
    "/alert-rules/{rule_id}/evaluate",
    response_model=EvaluationResultRead,
)
def evaluate_alert_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
):
    alert_rule = get_alert_rule_by_id(db, rule_id)

    if not alert_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found.",
        )

    stock = get_stock_by_id(db, alert_rule.stock_id)

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found for this alert rule.",
        )

    try:
        return evaluate_alert_rule(
            db=db,
            alert_rule=alert_rule,
            stock=stock,
        )
    except AlertEvaluationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc