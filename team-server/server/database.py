from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import time
import base64
from .utils import base64Decode, base64Encode, generateRandomStr

# Load environment variables
load_dotenv(".env")

# DB connection
db_user = os.environ["MYSQL_USER"]
db_password = os.environ["MYSQL_PASSWORD"]
db_database = os.environ["MYSQL_DATABASE"]
db_host = os.environ["MYSQL_HOST"]
db_engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_database}", echo=False)

# Database class; use for all operations
class HydrangeaDatabase():
    # Member data
    directoryUploads: str
    directoryDownloads: str

    # Constructor
    def __init__(self, directoryUploads: str, directoryDownloads: str):
        self.directoryUploads = directoryUploads
        self.directoryDownloads = directoryDownloads

    # Clear a table in database
    def clearTable(self, tableToClear: str):
        try:
            # Delete table
            with Session(db_engine) as session:
                session.execute(
                    text(f"DELETE FROM {tableToClear}")
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False

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
        
    # Get all agents
    def getAllAgents(self):
        try:
            with Session(db_engine) as session:
                return session.execute(
                    text("SELECT * FROM agents")
                ).fetchall()
        except SQLAlchemyError:
            return False
        
    # Save agent information
    def saveAgentInfo(self, agentId: str, host: str, username: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("INSERT INTO agents(id, host, username, lastCheckinAt) VALUES(:id, :host, :username, :lastCheckinAt)"),
                    [{
                        "id": agentId,
                        "host": host,
                        "username": username,
                        "lastCheckinAt": int(time.time())
                    }]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False
        
    # Update agent checkin timestamp
    def updateAgentTimestamp(self, agentId: str):
        try:
            with Session(db_engine) as session:
                session.execute(
                    text("UPDATE agents SET lastCheckinAt = :lastCheckinAt WHERE id = :id"),
                    [{
                        "id": agentId,
                        "lastCheckinAt": int(time.time())
                    }]
                )
                session.commit()
            return True
        except SQLAlchemyError:
            return False
        
    # Create new task
    def createNewTask(self, originClientId: str, agentId: str, task: str):
        try:
            with Session(db_engine) as session:
                # Intervention - pre-process specific Task types
                taskSplit = task.split("\x00")
                taskType = taskSplit[0]

                ## For file upload, save the file on Team server, and store file path to it in Database
                if taskType == "UPLOAD":
                    # Get filename
                    filePathOnTarget = taskSplit[2]
                    filePathOnTargetSplitByBackslash = filePathOnTarget.split("\\")
                    filePathOnTargetSplitByFrontslash = filePathOnTarget.split("/")
                    filename = None
                    if len(filePathOnTargetSplitByBackslash) != 0:
                        filename = filePathOnTargetSplitByBackslash[-1]
                    elif len(filePathOnTargetSplitByFrontslash) != 0:
                        filename = filePathOnTargetSplitByFrontslash[-1]
                    else:
                        filename = generateRandomStr(7)

                    # Write file on server, then store pathname to it in database
                    pathToSaveHereOnServer = os.path.join(self.directoryUploads, filename)
                    with open(pathToSaveHereOnServer, "wb+") as fileToSave:
                        fileToSave.write(base64Decode(taskSplit[1], outputString=False))
                    taskSplit[1] = pathToSaveHereOnServer
                    task = "\x00".join(taskSplit)

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
                # Get tasks
                tasks = session.execute(
                    text("SELECT * FROM tasks WHERE agentId = :agentId AND taskedAt IS NULL"),
                    [{
                        "agentId": agentId
                    }]
                ).fetchall()

                # Intervene - modify certain tasks
                tasksFinal: list[dict] = []
                for task in tasks:
                    taskSplit: list[str] = task.task.split("\x00")

                    ## For upload, replace file path with file contents
                    if taskSplit[0] == "UPLOAD":
                        try:
                            with open(taskSplit[1], "rb") as fileToSend:
                                fileContent = fileToSend.read()
                                fileContentB64 = base64.b64encode(fileContent).decode("utf-8")
                                taskSplit[1] = fileContentB64
                                taskProcessed = "\x00".join(taskSplit)

                                tasksFinal.append({
                                    "id": task.id,
                                    "originClientId": task.originClientId,
                                    "agentId": task.agentId,
                                    "task": taskProcessed,
                                    "output": task.output,
                                    "taskedAt": task.taskedAt,
                                    "outputAt": task.outputAt,
                                })
                        except Exception as e:
                            print(e)
                            pass

                    ## For all other tasks, just pass through
                    else:
                        tasksFinal.append({
                            "id": task.id,
                            "originClientId": task.originClientId,
                            "agentId": task.agentId,
                            "task": task.task,
                            "output": task.output,
                            "taskedAt": task.taskedAt,
                            "outputAt": task.outputAt,
                        })

                # Update taskedAt timestamp
                if setTasked:
                    session.execute(
                        text("UPDATE tasks SET taskedAt = :taskedAt WHERE agentId = :agentId AND taskedAt IS NULL"),
                        [{
                            "taskedAt": int(time.time()),
                            "agentId": agentId
                        }]
                    )
                    session.commit()

                return tasksFinal
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
        
    # Get all tasks initiated by particular client
    def getTasksInitiatedByClient(self, clientId: str, taskIdTillWhichSynced, onlyTasksWithOutput = False):
        try:
            with Session(db_engine) as session:
                if taskIdTillWhichSynced is None:
                    return session.execute(
                            text("SELECT * FROM tasks WHERE originClientId = :originClientId AND outputAt IS NOT NULL ORDER BY id ASC") if onlyTasksWithOutput
                            else text("SELECT * FROM tasks WHERE originClientId = :originClientId ORDER BY id ASC"),
                            [{
                                "originClientId": clientId
                            }]
                        ).fetchall()
                else:
                    return session.execute(
                            text("SELECT * FROM tasks WHERE originClientId = :originClientId AND id > :taskIdTillWhichSynced AND outputAt IS NOT NULL ORDER BY id ASC") if onlyTasksWithOutput
                            else text("SELECT * FROM tasks WHERE originClientId = :originClientId AND id > :taskIdTillWhichSynced ORDER BY id ASC"),
                            [{
                                "originClientId": clientId,
                                "taskIdTillWhichSynced": taskIdTillWhichSynced
                            }]
                        ).fetchall()
        except SQLAlchemyError:
            return False

    # Set task output
    def setTaskOutput(self, taskId: int, outputBytes: bytes):
        try:
            with Session(db_engine) as session:
                # Get existing task to update
                taskToUpdate = session.execute(
                        text("SELECT * FROM tasks WHERE id = :taskId"),
                        [{
                            "taskId": taskId
                        }]
                    ).fetchone()
                if taskToUpdate is not None:
                    task = taskToUpdate.task
                    taskSplit = task.split("\x00")
                    outputToSave = ""

                    # Intervention

                    ## For DOWNLOAD, save file content to disk and replace file contents by the saved file path
                    if taskSplit[0] == "DOWNLOAD":
                        ### Get filename
                        filePathOnTarget = taskSplit[1]
                        filePathOnTargetSplitByBackslash = filePathOnTarget.split("\\")
                        filePathOnTargetSplitByFrontslash = filePathOnTarget.split("/")
                        filename = None
                        if len(filePathOnTargetSplitByBackslash) != 0:
                            filename = filePathOnTargetSplitByBackslash[-1]
                        elif len(filePathOnTargetSplitByFrontslash) != 0:
                            filename = filePathOnTargetSplitByFrontslash[-1]
                        else:
                            filename = generateRandomStr(7)

                        ### Write file on server, then store pathname to it in database
                        pathToSaveHereOnServer = os.path.join(self.directoryDownloads, filename)
                        with open(pathToSaveHereOnServer, "wb+") as fileToSave:
                            fileToSave.write(outputBytes)
                        outputToSave = pathToSaveHereOnServer

                    ## For all other Tasks types, just save the Output data as is
                    else:
                        outputToSave = outputBytes.decode("utf-8")

                    # Perform update
                    session.execute(
                        text("UPDATE tasks SET output = :output, outputAt = :outputAt WHERE id = :taskId"),
                        [{
                            "output": outputToSave,
                            "outputAt": int(time.time()),
                            "taskId": taskId
                        }]
                    )
                    session.commit()

                    return True
                else:
                    return False
        except SQLAlchemyError:
            return False
