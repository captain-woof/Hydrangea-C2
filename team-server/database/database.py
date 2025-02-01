from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv(".env")

# DB connection
db_user = os.environ["MYSQL_USER"]
db_password = os.environ["MYSQL_PASSWORD"]
db_database = os.environ["MYSQL_DATABASE"]
db_host = os.environ["MYSQL_HOST"]
db_engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_database}", echo=True)

# Database class; use for all operations
class HydrangeaDatabase():
    # Create a new user
    def createUser(self, username: str, passwordHash: str, role: str):
        try:
            # Validate role
            if role not in ["admin", "operator", "observer"]:
                return False

            # Create user
            with Session(db_engine) as session:
                session.execute(
                    text("INSERT INTO users(username,password,role) VALUES(:username, :password, :role)"),
                    [{"username": username, "password": passwordHash, "role": role}]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False

    # Get user
    def getUserByUsername(self, username: str):
        try:
            with Session(db_engine) as session:
                user = session.execute(
                    text("SELECT * FROM users WHERE username=:username"),
                    [{"username": username}]
                )
                return user
        except SQLAlchemyError:
            return False
        
    # Change user password
    def changeUserPassword(self, username: str, passwordHashNew: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("UPDATE users SET password=:password WHERE username=:username"),
                    [{"password": passwordHashNew, "username": username}]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False
    
    # Change user username
    def changeUserUsername(self, username: str, usernameNew: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("UPDATE users SET username=:usernameNew WHERE username=:username"),
                    [{"usernameNew": usernameNew, "username": username}]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False
    
    # Change user role
    def changeUserRole(self, username: str, roleNew: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("UPDATE users SET role=:roleNew WHERE username=:username"),
                    [{"roleNew": roleNew, "username": username}]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False
        
    # Delete user
    def deleteUser(self, username: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("DELETE FROM users WHERE username=:username"),
                    [{"username": username}]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False