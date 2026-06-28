from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.core.database import SessionLocal
from app.services.scheduler_service import run_alert_evaluation_job


scheduler = BackgroundScheduler()


def scheduled_alert_job() -> None:
    db = SessionLocal()

    try:
        run_alert_evaluation_job(db=db)
    finally:
        db.close()


def start_scheduler() -> None:
    if not settings.SCHEDULER_ENABLED:
        return

    if scheduler.running:
        return

    scheduler.add_job(
        scheduled_alert_job,
        trigger="interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        id="marketpulse_alert_evaluation_job",
        replace_existing=True,
    )

    scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()