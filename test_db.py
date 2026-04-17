from backend import crud, models, schemas, database, security
from sqlalchemy.orm import Session

database.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()
try:
    # Test password hashing
    hashed = security.get_password_hash('test123')
    print(f'Password hashed successfully: {hashed[:20]}...')

    # Test user creation without stats
    user_data = schemas.UserCreate(name='test3', email='test3@example.com', password='test123')
    hashed_password = security.get_password_hash(user_data.password)
    db_user = models.User(name=user_data.name, email=user_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f'User created: {db_user.name}, {db_user.email}, id: {db_user.id}')

    # Test user stats creation
    user_stats = models.UserStats(user_id=db_user.id)
    db.add(user_stats)
    db.commit()
    db.refresh(user_stats)
    print(f'User stats created for user {db_user.id}')

    db.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    db.close()