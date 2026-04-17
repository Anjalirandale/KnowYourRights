from sqlalchemy.orm import Session

from . import models, schemas, security


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_stats = models.UserStats(user_id=db_user.id)
    db.add(user_stats)
    db.commit()
    db.refresh(user_stats)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user


def get_user_stats(db: Session, user_id: int):
    stats = db.query(models.UserStats).filter(models.UserStats.user_id == user_id).first()
    if stats is None:
        stats = models.UserStats(user_id=user_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


def update_stats(db: Session, user_id: int, stats: schemas.UserStatsCreate):
    user_stats = get_user_stats(db, user_id)
    user_stats.total_xp = stats.total_xp
    user_stats.level = stats.level
    user_stats.streak = stats.streak
    db.add(user_stats)
    db.commit()
    db.refresh(user_stats)
    return user_stats


def add_completed_scenario(db: Session, user_id: int, scenario: schemas.CompletedScenarioCreate):
    completed = models.CompletedScenario(
        user_id=user_id,
        scenario_id=scenario.scenario_id,
        domain=scenario.domain,
        correct=scenario.correct,
    )
    db.add(completed)
    db.commit()
    db.refresh(completed)
    return completed


def add_xp_entry(db: Session, user_id: int, entry: schemas.XPEntryCreate):
    xp = models.XPHistory(
        user_id=user_id,
        scenario_id=entry.scenario_id,
        domain=entry.domain,
        base_xp=entry.base_xp,
        streak_bonus=entry.streak_bonus,
        total_earned=entry.total_earned,
    )
    db.add(xp)
    db.commit()
    db.refresh(xp)
    return xp


def get_completed_scenarios(db: Session, user_id: int):
    return db.query(models.CompletedScenario).filter(models.CompletedScenario.user_id == user_id).all()


def get_xp_history(db: Session, user_id: int):
    return db.query(models.XPHistory).filter(models.XPHistory.user_id == user_id).all()
