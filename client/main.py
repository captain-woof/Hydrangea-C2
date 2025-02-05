from argparse import ArgumentParser
import help
from socket_custom import SocketCustom

########
# CLIENT
########

class Client():
    #########
    # MEMBERS
    #########
    host: str
    port: int
    socketClient: SocketCustom

    ###########
    # FUNCTIONS
    ###########

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def exit(self, errorCode = 0):
        self.socketClient.close()
        exit(errorCode)

    def start(self):
        try:
            # Connect to team server
            self.socketClient = SocketCustom()
            self.socketClient.connect((host, port))
            print(f"SUCCESS: Connected to team server {self.host}:{self.port}")

            # Authenticate
            username = input("Username: ")
            password = input("Password: ")
            self.socketClient.sendall(username.encode("utf-8") + b"\x00" + password.encode("utf-8"))
            authResponse = self.socketClient.recvall().decode("utf-8")
            print(authResponse)
            if authResponse.startswith("ERROR:"):
                self.exit()

            # Start client loop
            while True:
                # Take client input
                userInput = input(f"{username}@{self.host}:{self.port} > ")

                # Handle admin functions
                if userInput == "context admin":
                    # Admin functions loop
                    while True:
                        userInput = input(f"{username}@{self.host}:{self.port} > Admin > ")
                        # Print 'context admin' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_ADMIN)
                        # Go back from 'context admin'
                        elif userInput in ["back", "quit", "exit"]:
                            break
                        # Send command to server
                        else:
                            self.socketClient.sendall(userInput.encode("utf-8"))
                            response = self.socketClient.recvall().decode("utf-8")
                            print(response)

                # Handle listener functions
                elif userInput == "context listener":
                    # Listener functions loop
                    while True:
                        userInput = input(f"{username}@{self.host}:{self.port} > Listeners > ")
                        # Print 'context admin' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_LISTENER)
                        # Go back from 'context admin'
                        elif userInput in ["back", "quit", "exit"]:
                            break
                        # Send command to server
                        else:
                            self.socketClient.sendall(userInput.encode("utf-8"))
                            response = self.socketClient.recvall().decode("utf-8")
                            print(response)

                # Handle payload functions

                # Handle task functions

                # Handle quit to exit client
                elif userInput in ["quit", "exit"]:
                    self.socketClient.sendall(b"quit")
                    response = self.socketClient.recvall().decode("utf-8")
                    print(response)
                    self.exit()

                # Print 'main menu' help
                elif userInput == "help":
                    print(help.HELP_MAIN_MENU)

                # Handle listener function TODO

                # Handle payload function TODO

                # Wrong command
                else:
                    print("ERROR: Wrong command")
        except ConnectionRefusedError:
            print("ERROR: Failed to connect to server. Is server running?")

        except KeyboardInterrupt:
            print("SUCCESS: Quit")

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