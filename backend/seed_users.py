import sys
import os

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_users():
    db: Session = SessionLocal()
    users = [
        {"name": "Admin", "email": "admin@example.com", "password": "password123", "role": "admin"},
        {"name": "Approver", "email": "approver@example.com", "password": "password123", "role": "approver"},
        {"name": "Finance", "email": "finance@example.com", "password": "password123", "role": "finance"}
    ]

    for user_data in users:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            new_user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.add(new_user)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")
    
    db.commit()
    db.close()
    print("User seeding completed.")

if __name__ == "__main__":
    seed_users()
