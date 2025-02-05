from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import time

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
                ).first()
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
        
    # Create new task
    def createNewTask(self, originClientId: str, agentId: str, task: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("INSERT INTO tasks(originClientId, agentId, task) VALUES(:originClientId, :agentId, :task)"),
                    [{
                        "originClientId": originClientId,
                        "agentId": agentId,
                        "task": task
                    }]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False

    # Get new tasks for particular agent. optionally such new tasks are updated with "taskedAt" timestamp, so that next call will NOT return these tasks
    def getNewTasksForAgent(self, agentId: str, setTasked: bool = False):
        try:
            with Session(db_engine) as session:
                tasks = session.execute(
                    text("SELECT * FROM tasks WHERE agentId = :agentId AND taskedAt IS NULL"),
                    [{
                        "agentId": agentId
                    }]
                ).fetchall()

                if setTasked:
                    session.execute(
                        text("UPDATE tasks SET taskedAt = :taskedAt WHERE agentId = :agentId AND taskedAt IS NULL"),
                        [{
                            "taskedAt": int(time.time()),
                            "agentId": agentId
                        }]
                    )
                    session.commit()

                return tasks
        except SQLAlchemyError:
            return False
        
    # Get all tasks; optionally can filter by agent
    def getTasks(self, agentId: str = None):
        try:
            with Session(db_engine) as session:
                if agentId is not None:
                    return session.execute(
                        text("SELECT * FROM tasks WHERE agentId = :agentId"),
                        [{
                            "agentId": agentId
                        }]
                    ).fetchall()
                else:
                    return session.execute(
                        text("SELECT * FROM tasks"),
                        [{
                            "agentId": agentId
                        }]
                    ).fetchall()
        except SQLAlchemyError:
            return False

    # Set task output
    def setTaskOutput(self, taskId: int, output: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("UPDATE tasks SET output = :output, outputAt = :outputAt WHERE id = :taskId"),
                    [{
                        "output": output,
                        "outputAt": int(time.time()),
                        "taskId": taskId
                    }]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False

