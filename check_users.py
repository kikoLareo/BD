import sys
from sqlalchemy.orm import Session
from db.database import engine, SessionLocal
from models.models import User, Role, UserRole

def check_database():
    try:
        session = SessionLocal()
        
        # Check users
        users = session.query(User).all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")
        
        # Check roles
        roles = session.query(Role).all()
        print(f"\nTotal roles: {len(roles)}")
        for role in roles:
            print(f"Role: {role.name}, Description: {role.description}")
        
        # Check user roles
        user_roles = session.query(UserRole).all()
        print(f"\nTotal user roles: {len(user_roles)}")
        for user_role in user_roles:
            user = session.query(User).filter(User.id == user_role.user_id).first()
            role = session.query(Role).filter(Role.id == user_role.role_id).first()
            if user and role:
                print(f"User '{user.username}' has role '{role.name}'")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        session.close()

if __name__ == "__main__":
    check_database()
