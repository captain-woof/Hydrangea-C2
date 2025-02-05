from .socket_custom import SocketCustom
from database.database import HydrangeaDatabase
import base64

# Constants
LISTENER_COMMANDS_PREFIX = (
    "listenernew",
    "listenersget",
    "listenerdel"
)

# Handles Listener command; returns False if the input command is not a Task command
def handleListenerCommand(db: HydrangeaDatabase, socketClient: SocketCustom, clientId: str, user, userInput: str):
    # If command is for Listener, handle here
    if userInput.startswith(LISTENER_COMMANDS_PREFIX):
        # Check role
        if user.role not in ("operator", "admin"):
            socketClient.sendall(b"ERROR: Unauthorized")
        else:
            # Split command
            userInputSplit = userInput.split(" ")

            # Create new listener
            if userInput.startswith("listenernew"): # listenernew TYPE PORT -> LISTENER_ID
                if len(userInputSplit) == 1:
                    socketClient.sendall(b"ERROR: Invalid input")
                else:
                    pass

                    """
                    if db.createNewTask(
                        agentId=userInputSplit[1],
                        originClientId=clientId,
                        task=base64.b64decode(userInputSplit[2].encode("utf-8")).decode("utf-8")
                    ):
                        socketClient.sendall(f"SUCCESS: Task created for agent '{userInputSplit[1]}'".encode("utf-8"))
                    else:
                        socketClient.sendall(f"ERROR: Failed to create new task".encode("utf-8"))
                    """

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Listener
        return False