from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas, security
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KnowYourRights API",
    description="FastAPI backend for authentication and user progress tracking",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION_BANK = [
    {
        "id": 1,
        "question": "What should you do first if you suspect workplace discrimination?",
        "options": [
            "Ignore it and hope it stops",
            "Document the behavior and speak to HR",
            "Confront the person aggressively",
            "Quit immediately"
        ],
        "correct_answer": "Document the behavior and speak to HR",
        "explanation": "Documenting the behavior and speaking to HR creates a record and starts the resolution process.",
        "domain": "Workplace",
        "difficulty": "Easy",
        "xp_reward": 20,
        "legal_reference": "Employment Rights Act"
    },
    {
        "id": 2,
        "question": "If you receive a notice of eviction, how long do you typically have to respond?",
        "options": [
            "Immediately",
            "Within 24 hours",
            "Within the timeframe specified in the notice",
            "Within one year"
        ],
        "correct_answer": "Within the timeframe specified in the notice",
        "explanation": "Eviction notices always specify a deadline for response or compliance.",
        "domain": "Housing",
        "difficulty": "Medium",
        "xp_reward": 30,
        "legal_reference": "Tenant Rights Code"
    },
    {
        "id": 3,
        "question": "Which document helps you prove your identity for a loan application?",
        "options": [
            "A social media profile",
            "A government-issued photo ID",
            "A text message",
            "A utility bill without name"
        ],
        "correct_answer": "A government-issued photo ID",
        "explanation": "A government-issued photo ID is the standard proof of identity for financial applications.",
        "domain": "Consumer Rights",
        "difficulty": "Easy",
        "xp_reward": 20,
        "legal_reference": "Consumer Protection Act"
    },
]


@app.post("/auth/signup")
def signup(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    user = crud.create_user(db, user_create)
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user


@app.get("/api/user/progress", response_model=schemas.UserProgressResponse)
def read_user_progress(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    stats = crud.get_user_stats(db, current_user.id)
    completed = crud.get_completed_scenarios(db, current_user.id)
    xp_history = crud.get_xp_history(db, current_user.id)
    return {
        "user_stats": stats,
        "completed_scenarios": completed,
        "xp_history": xp_history,
    }


@app.put("/api/user/stats", response_model=schemas.UserStatsRead)
def update_user_stats(stats: schemas.UserStatsCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    updated = crud.update_stats(db, current_user.id, stats)
    return updated


@app.post("/api/user/completed-scenarios", response_model=schemas.CompletedScenarioRead)
def add_completed_scenario(scenario: schemas.CompletedScenarioCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    return crud.add_completed_scenario(db, current_user.id, scenario)


@app.post("/api/user/xp-history", response_model=schemas.XPEntryRead)
def add_xp_history(entry: schemas.XPEntryCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    return crud.add_xp_entry(db, current_user.id, entry)


@app.get("/questions", response_model=List[schemas.Question])
def list_questions(domain: str = "", difficulty: str = ""):
    filtered = QUESTION_BANK
    if domain:
        filtered = [q for q in filtered if q["domain"].lower() == domain.lower()]
    if difficulty:
        filtered = [q for q in filtered if q["difficulty"].lower() == difficulty.lower()]
    return filtered
