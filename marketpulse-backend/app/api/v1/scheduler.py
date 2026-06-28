from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.schemas.scheduler import SchedulerRunResultRead, SchedulerStatusRead
from app.services.scheduler_service import get_scheduler_status, run_alert_evaluation_job


router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"],
)


def validate_cron_secret(
    x_cron_secret: str | None = Header(default=None),
) -> None:
    if not settings.CRON_SECRET:
        return

    if x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing cron secret.",
        )


@router.post(
    "/run-once",
    response_model=SchedulerRunResultRead,
    dependencies=[Depends(validate_cron_secret)],
)
def run_scheduler_once_endpoint(
    db: Session = Depends(get_db),
):
    return run_alert_evaluation_job(db=db)


@router.get(
    "/status",
    response_model=SchedulerStatusRead,
)
def get_scheduler_status_endpoint():
    return get_scheduler_status()