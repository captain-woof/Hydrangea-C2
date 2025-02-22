from threading import Thread
from .socket_custom import SocketCustom
from . import admin as adminFunc
from . import agent as agentFunc
from . import auth as authFunc
from . import listener as listenerFunc
from . import sub as subscriptionFunc
from database.database import HydrangeaDatabase

class TeamServer():
    ##########
    # Members
    ##########
    host: str
    port: int
    db: HydrangeaDatabase
    socketServer: SocketCustom
    listenersMap: dict # Listener_ID -> (LISTENER_LAUNCHER)
    clientIdToAgentsNotificationMap = {} # clientId -> [agentId1, agentId2]
    clientIdToLatestTaskIdSyncedMap = {} # clientId -> TASK_ID; since task ids are sequential, this helps to filter for new tasks

    ##########
    # Methods
    ##########

    # Constructor
    def __init__(self, host: str = "127.0.0.1", port: int = 6060):
        self.host = host
        self.port = port
        self.db = HydrangeaDatabase()
        self.listenersMap = {}

    # Register new listener
    def registerListener(self, listenerId: str, listenerLauncher):
        if self.listenersMap.get(listenerId) is None:
            self.listenersMap[listenerId] = (listenerLauncher)
            return True
        else:
            return False

    # Remove existing listener
    def removeListener(self, listenerId: str):
        if self.listenersMap.get(listenerId) is None:
            return False
        else:
            self.listenersMap[listenerId].stop()
            del self.listenersMap[listenerId]
            return True
        
    # Disconnect from client
    def closeClientConnection(self, clientId: str, socketClient: SocketCustom):
        # To quit publisher thread and subscriber client socket
        if clientId is not None:
            if self.clientIdToAgentsNotificationMap.get(clientId) is not None:
                self.clientIdToAgentsNotificationMap[clientId] = "stop"
            if self.clientIdToLatestTaskIdSyncedMap.get(clientId) is not None:
                self.clientIdToLatestTaskIdSyncedMap[clientId] = "stop"

        # Close interactive client socket
        if socketClient is not None:
            socketClient.sendall(b"SUCCESS: Bye from team server")
            socketClient.close()

    # Handle independent session in Thread
    def startSession(self, socketClient: SocketCustom, addrClient: tuple):
        try:
            print(f"SUCCESS: Starting session from {addrClient[0]}:{addrClient[1]}")

            # Authentication
            user, clientId = authFunc.handleAuth(db=self.db, socketClient=socketClient, addrClient=addrClient)
            if user is None:
                return
            
            try:
                # Start client handling loop
                while True:
                    # Receive all user data
                    userInputRaw = socketClient.recvall()
                    if userInputRaw is None:
                        continue
                    userInput = userInputRaw.decode("utf-8")

                    # Quit
                    if userInput in ["quit", "exit"]: # User wants to quit
                        self.closeClientConnection(
                            clientId=clientId,
                            socketClient=socketClient
                        )
                        break

                    # If subscription command, handle it. Upon exit, break loop
                    elif subscriptionFunc.handleSubscriptionCommand(db=self.db, socketClient=socketClient, user=user, userInput=userInput, clientIdToAgentsNotificationMap=self.clientIdToAgentsNotificationMap, clientIdToLatestTaskIdSyncedMap=self.clientIdToLatestTaskIdSyncedMap):
                        self.closeClientConnection(
                            clientId=clientId,
                            socketClient=socketClient
                        )
                        break

                    # If admin command, handle it and go back to start
                    elif adminFunc.handleAdminCommand(db=self.db, socketClient=socketClient, user=user, userInput=userInput):
                        continue

                    # If listener command, handle it and go back to start
                    elif listenerFunc.handleListenerCommand(db=self.db, clientId=clientId, socketClient=socketClient, user=user, userInput=userInput, registerListener=self.registerListener, removeListener=self.removeListener, listenersMap=self.listenersMap):
                        continue

                    # If agent command, handle it and go back to start
                    elif agentFunc.handleAgentCommand(db=self.db, clientId=clientId, socketClient=socketClient, user=user, userInput=userInput):
                        continue

                    # Wrong command if execution reaches here
                    socketClient.sendall(b"ERROR: Wrong command")
            except Exception as e:
                print(e)
                self.closeClientConnection(
                    clientId=clientId,
                    socketClient=socketClient
                )
        except Exception as e:
            print(e)
            self.closeClientConnection(
                clientId=None,
                socketClient=socketClient
            )

    # Stop server
    def stop(self):
        # To quit all publisher threads
        for k in self.clientIdToAgentsNotificationMap.keys():
            self.clientIdToAgentsNotificationMap[k] = "stop"
        for k in self.clientIdToLatestTaskIdSyncedMap.keys():
            self.clientIdToLatestTaskIdSyncedMap[k] = "stop"

        # Close server socket
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

            # Start independent session
            thread = Thread(
                target=self.startSession,
                kwargs={
                    "socketClient": socketClient,
                    "addrClient": addrClient
                }
            )
            thread.start()
