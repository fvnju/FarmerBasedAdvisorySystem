from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import AlertChannel, AlertStatus, db_enum  # Import enums


class Alert(Base):  # A weather action alert. Send only if the user has consent for alerts.
    __tablename__ = "alerts"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # User who gets the alert
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True
    )  # Farm the alert is about
    response_id = Column(
        Integer, ForeignKey("advisory_responses.id", ondelete="SET NULL"), nullable=True
    )  # Advice that caused the alert
    weather_forecast_id = Column(
        Integer, ForeignKey("weather_forecasts.id", ondelete="SET NULL"), nullable=True
    )  # Forecast that caused the alert
    channel = Column(db_enum(AlertChannel), nullable=False)  # Delivery channel
    title = Column(String(150), nullable=False)  # Short heading
    message = Column(Text, nullable=False)  # Alert text
    dedupe_key = Column(
        String(150), unique=True, nullable=False
    )  # For example "<farm>:<rule>:<date>", stops duplicate alerts
    status = Column(
        db_enum(AlertStatus), nullable=False, server_default=AlertStatus.PENDING.value, index=True
    )  # Delivery state
    scheduled_for = Column(DateTime, nullable=False, index=True)  # Time to send
    sent_at = Column(DateTime, nullable=True)  # Time the alert was sent
    expires_at = Column(DateTime, nullable=True)  # Do not send after this time
    read_at = Column(DateTime, nullable=True)  # Time the user opened it
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Entry time

    user = relationship("User")  # Recipient
    farm = relationship("Farm")  # Farm
