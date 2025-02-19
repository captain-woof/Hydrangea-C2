from argparse import ArgumentParser
import help
from socket_custom import SocketCustom
import base64
from threading import Thread

#########
# HELPERS
#########

def base64Encode(s: str):
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")

def base64Decode(s: str):
    return base64.b64decode(s.encode("utf-8")).decode("utf-8")

def stringSplitAdvanced(strInput):
    """
    Splits a UTF-8 string by spaces, treating substrings enclosed in " or ' as single units.
    Escaped quotes (\\", \\') within their respective quotes do not end the substring.

    Args:
        input_string: The UTF-8 string to split.

    Returns:
        A list of strings representing the split result.
    """
    result = []
    current_word = ""
    quote_type = None  # None, '"', or "'"
    escape = False

    for char in strInput:
        if escape:
            current_word += char
            escape = False
            continue

        if char == '\\':
            escape = True
            continue

        if quote_type:  # Inside a quote
            if char == quote_type:
                result.append(current_word)
                current_word = ""
                quote_type = None
            else:
                current_word += char
        else:  # Not inside a quote
            if char == ' ':
                if current_word:  # Add word if it's not empty
                    result.append(current_word)
                    current_word = ""
            elif char == '"':
                quote_type = '"'
                current_word = "" # Start a new word
            elif char == "'":
                quote_type = "'"
                current_word = "" # Start a new word
            else:
                current_word += char

    # Add the last word if any
    if current_word:
        result.append(current_word)

    return result

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
                                        stringSplitAdvanced(userInput)
                                        stringSplitAdvanced[0] = stringSplitAdvanced[0].upper() # Command name
                                        taskByteEncoded = b"\x00".join(stringSplitAdvanced.map(lambda x: x.encode("utf-8"))) # b"COMMAND\x00PARAM1\x00PARAM2"
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
            self.exit()
            print("ERROR: Quitting due to error")

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