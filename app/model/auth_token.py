from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func  # Import column tools
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import TokenPurpose, db_enum  # Import token purposes


class RefreshToken(Base):  # One login session on one device
    __tablename__ = "refresh_tokens"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Owner of the session
    token_hash = Column(
        String(255), unique=True, nullable=False
    )  # SHA-256 of the token, never the token itself
    expires_at = Column(DateTime, nullable=False)  # Token stops working after this time
    revoked_at = Column(DateTime, nullable=True)  # Set on logout or rotation
    replaced_by_id = Column(
        Integer, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
    )  # Next token in a rotation, to detect reuse
    user_agent = Column(String(255), nullable=True)  # Browser or device description
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Issue time

    user = relationship("User", back_populates="refresh_tokens")  # Owner


class OneTimeToken(Base):  # Token for email or phone verification and password reset
    __tablename__ = "one_time_tokens"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Owner of the token
    purpose = Column(db_enum(TokenPurpose), nullable=False)  # What the token is for
    token_hash = Column(
        String(255), unique=True, nullable=False
    )  # SHA-256 of the token or code
    expires_at = Column(DateTime, nullable=False)  # Token stops working after this time
    used_at = Column(DateTime, nullable=True)  # Set when the token is used
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Issue time

    user = relationship("User", back_populates="one_time_tokens")  # Owner
