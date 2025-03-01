from argparse import ArgumentParser
import help
from socket_custom import SocketCustom
from threading import Thread
import json
from utils import *

########
# CLIENT
########

class Client():
    #########
    # MEMBERS
    #########
    host: str = ""
    port: int = 0
    socketClient: SocketCustom = None
    socketSubscriber: SocketCustom = None
    threadSubscriber: Thread = None

    ###########
    # FUNCTIONS
    ###########

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    # Close connection
    def exit(self, errorCode = 0):
        quitResponse = self.sendAndReceiveFromTeamServer("quit")
        if quitResponse is not None:
            print(quitResponse)

        if self.socketSubscriber is not None:
            self.socketSubscriber.close()

        if self.threadSubscriber is not None:    
            self.threadSubscriber.join()

        if self.socketClient is not None:    
            self.socketClient.close()
        exit(errorCode)

    # Send interactive command and receive output from team-server
    def sendAndReceiveFromTeamServer(self, whatToSend):
        self.socketClient.sendall(whatToSend.encode("utf-8") if type(whatToSend) is str else whatToSend)
        response = self.socketClient.recvall()

        if response is None:
            return None
        else:
            responseDecoded = response.decode("utf-8")

            # If response is a JSON, show in table
            try:
                responseDecodedJson = json.loads(responseDecoded)

                # If single json object, convert to array of json
                if isinstance(responseDecodedJson, dict):
                    responseDecodedJson = [responseDecodedJson]

                # If there are any base64 values, decode them in place
                for rowIndex, row in enumerate(responseDecodedJson):
                    for key,val in row.items():
                        if key not in ("taskB64", "outputB64"):
                            continue
                        try:
                            valB64Decoded = base64Decode(val)
                            responseDecodedJson[rowIndex][key] = valB64Decoded
                        except Exception:
                            continue

                # If there are any time-like values, convert them in place to readable format
                for rowIndex, row in enumerate(responseDecodedJson):
                    for key,val in row.items():
                        if key not in ("taskedAt", "outputAt", "lastCheckinAt"):
                            continue
                        try:
                            if val in (None, 0, "0"):
                                responseDecodedJson[rowIndex][key] = ""
                            else:
                                valHumanReadableTime = convertUnixTimeToHumanReadable(val)                            
                                responseDecodedJson[rowIndex][key] = valHumanReadableTime
                        except Exception:
                            continue          

                # Create and put everything in a table
                return dictArrayToTable(responseDecodedJson)
            except Exception:
                pass

            # Else return as is
            return responseDecoded
    
    # Subscription handler
    def streamMessages(self, host: str, port: int, username: str, password: str, clientIdToSubscribeFor: str):
        try:
            self.socketSubscriber = SocketCustom()
            self.socketSubscriber.connect((host, port))

            self.socketSubscriber.sendall(username.encode("utf-8") + b"\x00" + password.encode("utf-8"))
            authResponse = self.socketSubscriber.recvall().decode("utf-8")
            if authResponse.startswith("ERROR:"):
                print("ERROR: Failed to subscribe for messages")
            else:
                self.socketSubscriber.sendall(f"subscribe {clientIdToSubscribeFor}".encode("utf-8"))
                while True:
                    print("\n" + self.socketSubscriber.recvall().decode("utf-8"))
        except Exception:
            print(f"INFO: Ending subscription for client ID '{clientIdToSubscribeFor}'")
        
    # Subscribes for messages
    def subscribeForUpdates(self, username: str, password: str, clientId: str):
        self.threadSubscriber = Thread(
            target=self.streamMessages,
            kwargs={
                "host": self.host,
                "port": self.port,
                "username": username,
                "password": password,
                "clientIdToSubscribeFor": clientId
            }
        )
        self.threadSubscriber.start()

    def start(self):
        try:
            # Connect to team server
            self.socketClient = SocketCustom()
            self.socketClient.connect((host, port))
            print(f"SUCCESS: Connected to team server {self.host}:{self.port}")

            # Authenticate
            username = input("Username: ")
            password = input("Password: ")
            authResponse = self.sendAndReceiveFromTeamServer(username.encode("utf-8") + b"\x00" + password.encode("utf-8"))
            if authResponse is None:
                self.exit()
            print(authResponse)
            if authResponse.startswith("ERROR:"):
                self.exit()
            clientId = authResponse.split("'")[1]

            # Start subscription loop for client ID
            self.subscribeForUpdates(username=username, password=password, clientId=clientId)

            # Start client loop
            while True:
                # Take client input
                userInput = input(f"{username}@{self.host}:{self.port} > ")
                if userInput == "":
                    continue

                # Handle admin functions
                if userInput == "context admin":
                    # Admin functions loop
                    while True:
                        userInput = input(f"{username}@{self.host}:{self.port} > Admin > ")
                        if userInput == "":
                            continue
                        # Print 'context admin' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_ADMIN)
                        # Go back from 'context admin'
                        elif userInput in ["back", "quit", "exit"]:
                            break
                        # Send command to server
                        else:
                            print(self.sendAndReceiveFromTeamServer(userInput))

                # Handle listener functions
                elif userInput == "context listener":
                    # Listener functions loop
                    while True:
                        userInput = input(f"{username}@{self.host}:{self.port} > Listeners > ")
                        if userInput == "":
                            continue
                        # Print 'context listener' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_LISTENER)
                        # Go back from 'context listener'
                        elif userInput in ["back", "quit", "exit"]:
                            break
                        # Send command to server
                        else:
                            print(self.sendAndReceiveFromTeamServer(userInput))

                # Handle payload functions TODO

                # Handle agent functions
                elif userInput == "context agent":
                    # Agent functions loop
                    while True:
                        userInput = input(f"{username}@{self.host}:{self.port} > Agents > ")
                        if userInput == "":
                            continue

                        # Print 'context agent' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_AGENT)

                        # Go back from 'context agent'
                        elif userInput in ["back", "quit", "exit"]:
                            break

                        # Send command to server
                        else:
                            userInputSplit = userInput.split(" ")

                            # List all agents; agentsget
                            if userInputSplit[0] == "agentsget":
                                print(self.sendAndReceiveFromTeamServer("agentsget"))

                            # Get all tasks of all agents; agentstasksget
                            elif userInputSplit[0] == "agentstasksget":
                                print(self.sendAndReceiveFromTeamServer("tasksget"))

                            # Interact with agent; agentinteract AGENT_ID
                            elif userInputSplit[0] == "agentinteract":
                                agentId = userInputSplit[1]
                                while True:
                                    userInput = input(f"{username}@{self.host}:{self.port} > Agents > {agentId}$ ")
                                    if userInput == "":
                                        continue

                                    # Go back if needed
                                    if userInput in ["back", "quit"]:
                                        break

                                    # Help
                                    elif userInput == "help":
                                        print(help.HELP_CONTEXT_AGENT_CAPABILITIES)

                                    # Get all tasks of agent
                                    elif userInput == "tasksget":
                                        dataToSend = f"tasksget {agentId}"
                                        print(self.sendAndReceiveFromTeamServer(dataToSend))
                                    
                                    # Create new task for agent
                                    else:
                                        userInputSplit = stringSplitAdvanced(userInput)

                                        # Uppercase task type
                                        userInputSplit[0] = userInputSplit[0].upper() # Command name

                                        # Intervention

                                        ## For upload file, replace file path with base64 of file content
                                        if userInputSplit[0] == "UPLOAD":
                                            fileToSendPath = userInputSplit[1]
                                            try:
                                                with open(fileToSendPath, "rb") as fileToSend:
                                                    fileToSendContentB64 = base64Encode(fileToSend.read())
                                                    userInputSplit[1] = fileToSendContentB64
                                            except FileNotFoundError:
                                                print(f"ERROR: '{fileToSendPath}' does not exist")
                                                continue
                                            except Exception as e:
                                                print(f"ERROR:", e)
                                                continue

                                        taskByteEncoded = b"\x00".join(map(lambda x: x.encode("utf-8"), userInputSplit)) # b"COMMAND\x00PARAM1\x00PARAM2"
                                        dataToSend = f"tasknew {agentId} {base64Encode(taskByteEncoded)}"
                                        print(self.sendAndReceiveFromTeamServer(dataToSend))
            
                            # Wrong command
                            else:
                                print("ERROR: Invalid command") 

                # Handle quit to exit client
                elif userInput in ["quit", "exit"]:
                    self.exit()

                # Print 'main menu' help
                elif userInput == "help":
                    print(help.HELP_MAIN_MENU)

                # Wrong command
                else:
                    print("ERROR: Wrong command")
        except ConnectionRefusedError:
            print("ERROR: Failed to connect to server. Is server running?")

        except KeyboardInterrupt:
            self.exit()
            print("SUCCESS: Quit")

        except Exception as e:
            print(e)
            print("ERROR: Quitting due to error")
            self.exit()

########
# MAIN
########

if __name__ == "__main__":
    # Define command line args
    parser = ArgumentParser(description="Starts Hydrangea C2 client")
    parser.add_argument("-H", "--host", action="store", default="127.0.0.1", help="Hydrangea C2's team server hostname/IP; default: 127.0.0.1")
    parser.add_argument("-P", "--port", action="store", type=int, default=6060, help="Hydrangea C2's team server port; default: 6060")
    args = parser.parse_args()

    host = args.host
    port = args.port

    # Start client
    client = Client(host=host, port=port)
    client.start()