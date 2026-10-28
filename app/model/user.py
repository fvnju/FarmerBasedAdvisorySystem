from sqlalchemy import Boolean, Column, DateTime, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.mixins import TimestampMixin  # Import created_at and updated_at


class User(TimestampMixin, Base):  # Define User model
    __tablename__ = "users"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    username = Column(
        String(50), unique=True, index=True, nullable=False
    )  # Username field
    email = Column(String(100), unique=True, index=True, nullable=False)  # Email field
    phone_number = Column(
        String(20), unique=True, index=True, nullable=True
    )  # Phone in E.164 format, for SMS alerts and login
    hashed_password = Column(String(255), nullable=False)  # Password hash, never plain text
    full_name = Column(String(150), nullable=True)  # Display name
    preferred_language = Column(
        String(10), nullable=False, server_default="en"
    )  # Language code for advice, for example "en" or "ha"
    is_active = Column(
        Boolean, nullable=False, server_default="1"
    )  # False blocks login without a delete
    email_verified_at = Column(DateTime, nullable=True)  # Set when the email is confirmed
    phone_verified_at = Column(DateTime, nullable=True)  # Set when the phone is confirmed
    last_login_at = Column(DateTime, nullable=True)  # Last successful login

    roles = relationship(
        "Role", secondary="user_role", back_populates="users"
    )  # Many-to-many relationship
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )  # Login sessions
    one_time_tokens = relationship(
        "OneTimeToken", back_populates="user", cascade="all, delete-orphan"
    )  # Verification and reset tokens
    consents = relationship(
        "ConsentRecord",
        foreign_keys="ConsentRecord.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )  # Consent history
    farms = relationship("Farm", back_populates="owner")  # Farms this user owns
    assigned_farmers = relationship(
        "AgentFarmerAssignment",
        foreign_keys="AgentFarmerAssignment.agent_id",
        back_populates="agent",
    )  # Farmers this extension agent helps
    assigned_agents = relationship(
        "AgentFarmerAssignment",
        foreign_keys="AgentFarmerAssignment.farmer_id",
        back_populates="farmer",
    )  # Agents that help this farmer
