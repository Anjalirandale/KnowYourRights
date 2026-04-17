from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stats = relationship("UserStats", back_populates="user", uselist=False)
    completed_scenarios = relationship("CompletedScenario", back_populates="user")
    xp_history = relationship("XPHistory", back_populates="user")


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)

    user = relationship("User", back_populates="stats")


class CompletedScenario(Base):
    __tablename__ = "completed_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, nullable=True)
    domain = Column(String, nullable=True)
    correct = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="completed_scenarios")


class XPHistory(Base):
    __tablename__ = "xp_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, nullable=True)
    domain = Column(String, nullable=True)
    base_xp = Column(Integer, nullable=False)
    streak_bonus = Column(Integer, nullable=False)
    total_earned = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="xp_history")
