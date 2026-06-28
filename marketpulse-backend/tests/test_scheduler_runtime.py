from unittest.mock import patch

from app.core.scheduler import scheduler, shutdown_scheduler, start_scheduler


def test_start_scheduler_does_not_start_when_disabled():
    if scheduler.running:
        shutdown_scheduler()

    with patch("app.core.scheduler.settings.SCHEDULER_ENABLED", False):
        start_scheduler()

    assert scheduler.running is False


def test_start_scheduler_starts_when_enabled():
    if scheduler.running:
        shutdown_scheduler()

    with patch("app.core.scheduler.settings.SCHEDULER_ENABLED", True), patch(
        "app.core.scheduler.settings.SCHEDULER_INTERVAL_MINUTES",
        15,
    ):
        start_scheduler()

    assert scheduler.running is True

    shutdown_scheduler()

    assert scheduler.running is False


def test_shutdown_scheduler_is_safe_when_not_running():
    if scheduler.running:
        shutdown_scheduler()

    shutdown_scheduler()

    assert scheduler.running is False