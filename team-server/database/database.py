from dotenv import load_dotenv
import os
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

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
    def createUser(self, username: str, password: str, role: str):
        # Validate role
        if role not in ["admin", "operator", "observer"]:
            return False
        
        # Hash user password
        passwordHash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Create user
        with Session(db_engine) as session:
            session.execute(
                text("INSERT INTO users(username,password,role) VALUES(:username, :password, :role)"),
                [{"username": username, "password": passwordHash, "role": role}]
            )

    # Get user
    def getUserByUsername(self, username: str):
        with Session(db_engine) as session:
            user = session.execute(
                text("SELECT * FROM users WHERE username=:username"),
                [{"username": username}]
            )

            return user
