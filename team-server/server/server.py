from threading import Thread
from .socket_custom import SocketCustom
from . import admin as adminFunc
from . import task as taskFunc
from . import auth as authFunc
from . import listener as listenerFunc
from database.database import HydrangeaDatabase

class TeamServer():
    ##########
    # Members
    ##########
    host: str
    port: int
    maxConns: int
    sessions: dict # TODO
    db: HydrangeaDatabase
    socketServer: SocketCustom

    ##########
    # Methods
    ##########

    # Constructor
    def __init__(self, host: str = "127.0.0.1", port: int = 6060, maxConns: int = 20):
        self.host = host
        self.port = port
        self.maxConns = maxConns
        self.db = HydrangeaDatabase()

    # Handle independent session in Thread
    def startSession(self, socketClient: SocketCustom, addrClient: tuple):
        print(f"SUCCESS: Starting session from {addrClient[0]}:{addrClient[1]}")

        # Authentication
        user = authFunc.handleAuth(db=self.db, socketClient=socketClient)
        if user is None:
            return
        clientId = f"{user.username}-{addrClient[0]}:{addrClient[1]}"

        # Start client handling loop
        while True:
            # Receive all user data
            userInputRaw = socketClient.recvall()
            if userInputRaw is None:
                continue
            userInput = userInputRaw.decode("utf-8")

            # Quit
            if userInput in ["quit", "exit"]: # User wants to quit
                socketClient.sendall(b"Bye")
                socketClient.close()
                return

            # If admin command, handle it and go back to start
            if adminFunc.handleAdminCommand(db=self.db, socketClient=socketClient, user=user, userInput=userInput):
                continue

            # If listener command, handle it and go back to start
            if listenerFunc.handleListenerCommand(db=self.db, clientId=clientId, socketClient=socketClient, user=user, userInput=userInput):
                continue

            # If task command, handle it and go back to start
            if taskFunc.handleTaskCommand(db=self.db, clientId=clientId, socketClient=socketClient, user=user, userInput=userInput):
                continue

            # Wrong command if execution reaches here
            socketClient.sendall(b"ERROR: Wrong command")

    # Stop server
    def stop(self):
        self.socketServer.close()

    # Start server
    def start(self):
        # Initialise server socket
        self.socketServer = SocketCustom()
        self.socketServer.bind((self.host, self.port))
        print(f"Team Server listening on {self.host}:{self.port}")

        # Server loop
        while True:
            self.socketServer.listen()
            socketClient, addrClient = self.socketServer.accept()

            # Start independent session; TODO: handle session num limiting
            thread = Thread(
                target=self.startSession,
                kwargs={
                    "socketClient": socketClient,
                    "addrClient": addrClient
                }
            )
            thread.start()
