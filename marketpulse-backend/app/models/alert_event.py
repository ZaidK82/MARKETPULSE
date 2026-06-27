from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    alert_rule_id: Mapped[int] = mapped_column(
        ForeignKey("alert_rules.id"),
        nullable=False,
        index=True,
    )

    stock_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    triggered_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    alert_rule = relationship(
        "AlertRule",
        back_populates="alert_events",
    )

    notification_logs = relationship(
        "NotificationLog",
        back_populates="alert_event",
        cascade="all, delete-orphan",
    )