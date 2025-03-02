from .socket_custom import SocketCustom
from .database import HydrangeaDatabase
from listeners.http.launcher import HttpListenerLauncher

# Constants
LISTENER_COMMANDS_PREFIX = (
    "listenernew",
    "listenersget",
    "listenerdel"
)

# Handles Listener command; returns False if the input command is not a Task command
def handleListenerCommand(db: HydrangeaDatabase, socketClient: SocketCustom, clientId: str, user, userInput: str, registerListener, removeListener, listenersMap: dict, directoryDownloads: str, directoryUploads: str):
    # If command is for Listener, handle here
    if userInput.startswith(LISTENER_COMMANDS_PREFIX):
        # Check role
        if user.role not in ("operator", "admin"):
            socketClient.sendall(b"ERROR: Unauthorized")
        else:
            # Split command
            userInputSplit = userInput.split(" ")

            # Create new listener
            if userInput.startswith("listenernew"): # listenernew TYPE HOST PORT -> LISTENER_ID
                if len(userInputSplit) == 1:
                    socketClient.sendall(b"ERROR: Invalid input")
                else:
                    typeOfListener = userInputSplit[1]

                    # HTTP Listener
                    if typeOfListener == "http":
                        listenerId = f"http://{userInputSplit[2]}:{userInputSplit[3]}"

                        httpListenerLauncher = HttpListenerLauncher(
                            host=userInputSplit[2],
                            port=int(userInputSplit[3]),
                            workersNum=1,
                            directoryUploads=directoryUploads,
                            directoryDownloads=directoryDownloads
                        )
                        if not httpListenerLauncher.start(streamOutput=True):
                            socketClient.sendall(f"ERROR: Failed to start HTTP listener process for '{listenerId}'".encode("utf-8"))
                        else:
                            if registerListener(
                                listenerId = listenerId,
                                listenerLauncher = httpListenerLauncher
                            ):
                                socketClient.sendall(f"SUCCESS: HTTP listener started; Listener ID = '{listenerId}'".encode("utf-8"))
                            else:
                                socketClient.sendall(f"ERROR: Failed to register HTTP listener for '{listenerId}'".encode("utf-8"))
                    
                    # Invalid listener type
                    else:
                        socketClient.sendall(f"ERROR: Invalid listener type".encode("utf-8"))

            # Get all listeners
            elif userInput.startswith("listenersget"): # listenersget
                listenersNum = len(listenersMap.keys())

                listenersResult = ""
                for listenerId, listenerData in listenersMap.items():
                    listenersResult += f"- {listenerId}\n"

                socketClient.sendall(f"SUCCESS: {listenersNum} listeners started\n{listenersResult}".encode("utf-8"))
            
            # Delete existing listener
            elif userInput.startswith("listenerdel"): # listenerdel LISTENER_ID
                listenersNum = len(listenersMap.keys())

                if len(userInputSplit) != 2:
                    socketClient.sendall(f"ERROR: Invalid arguments".encode("utf-8"))
                else:
                    if removeListener(
                        listenerId = userInputSplit[1]
                    ):
                        socketClient.sendall(f"SUCCESS: HTTP listener stopped".encode("utf-8"))
                    else:
                        socketClient.sendall(f"ERROR: Failed to stop HTTP listener".encode("utf-8"))

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Listener
        return False