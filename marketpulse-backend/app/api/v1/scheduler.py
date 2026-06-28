from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scheduler import SchedulerRunResultRead, SchedulerStatusRead
from app.services.scheduler_service import get_scheduler_status, run_alert_evaluation_job


router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"],
)


@router.post(
    "/run-once",
    response_model=SchedulerRunResultRead,
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