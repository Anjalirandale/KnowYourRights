from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[EmailStr] = None


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserStatsBase(BaseModel):
    total_xp: int
    level: int
    streak: int


class UserStatsCreate(UserStatsBase):
    pass


class UserStatsRead(UserStatsBase):
    class Config:
        from_attributes = True


class CompletedScenarioBase(BaseModel):
    scenario_id: Optional[int] = None
    domain: Optional[str] = None
    correct: bool


class CompletedScenarioCreate(CompletedScenarioBase):
    pass


class CompletedScenarioRead(CompletedScenarioBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class XPEntryBase(BaseModel):
    scenario_id: Optional[int] = None
    domain: Optional[str] = None
    base_xp: int
    streak_bonus: int
    total_earned: int


class XPEntryCreate(XPEntryBase):
    pass


class XPEntryRead(XPEntryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class UserProgressResponse(BaseModel):
    user_stats: UserStatsRead
    completed_scenarios: List[CompletedScenarioRead]
    xp_history: List[XPEntryRead]


class Question(BaseModel):
    id: int
    question: str
    domain: str
    difficulty: str
    choices: List[str]
    answer: str
