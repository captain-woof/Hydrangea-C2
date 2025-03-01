from .database import HydrangeaDatabase
from .socket_custom import SocketCustom
from time import sleep, time
from .utils import convertUnixTimeToHumanReadable

# Constants
SUBSCRIPTION_COMMANDS_PREFIX = (
    "subscribe"
)

# Handles Subscription command and communicates result to client; returns False if the input command is not an Subscription command
def handleSubscriptionCommand(db: HydrangeaDatabase, socketClient: SocketCustom, user, userInput: str, clientIdToAgentsNotificationMap: dict, clientIdToLatestTaskIdSyncedMap: dict):
    # If command is for Administration, handle here
    if userInput.startswith(SUBSCRIPTION_COMMANDS_PREFIX):
        # Split command
        userInputSplit = userInput.split(" ")

        # New user
        if userInput.startswith("subscribe"): # subscribe CLIENT_ID
            clientId = userInputSplit[1]

            # Initialise synced messages
            ## For new agents
            if clientIdToAgentsNotificationMap.get(clientId) is None:
                clientIdToAgentsNotificationMap[clientId] = []
            ## For new task outputs
            if clientIdToLatestTaskIdSyncedMap.get(clientId) is None:
                clientIdToLatestTaskIdSyncedMap[clientId] = 0

            # Start publish loop
            while True:
                # Check if subscription thread should stop
                if clientIdToAgentsNotificationMap[clientId] == "stop" or clientIdToLatestTaskIdSyncedMap[clientId] == "stop":
                    socketClient.sendall(f"SUCCESS: Publisher closing on Team server".encode("utf-8")) 
                    break

                # Notify for all new agents
                agentsAll = db.getAllAgents()
                agentsToNotifyAbout = []

                for agent in agentsAll:
                    if agent.id not in clientIdToAgentsNotificationMap[clientId]:
                        clientIdToAgentsNotificationMap[clientId].append(agent.id)
                        agentsToNotifyAbout.append(agent)
                if len(agentsToNotifyAbout) != 0:
                    notificationMessage = ""
                    for agent in agentsToNotifyAbout:
                        notificationMessage += f"- Agent {agent.id}; {agent.username}@{agent.host}; last checkin {int(time()) - int(agent.lastCheckinAt)} secs ago\n"
                    socketClient.sendall(f"SUCCESS: New agents joined\n{notificationMessage}".encode("utf-8"))                   
                
                # Notify for new task outputs; show only tasks started by client ID
                tasksToNotifyAbout = db.getTasksInitiatedByClient(
                    clientId=clientId,
                    taskIdTillWhichSynced=clientIdToLatestTaskIdSyncedMap[clientId],
                    onlyTasksWithOutput=True
                )
                if len(tasksToNotifyAbout) != 0:
                    clientIdToLatestTaskIdSyncedMap[clientId] = tasksToNotifyAbout[-1].id
                    notificationMessage = ""
                    for task in tasksToNotifyAbout:
                        # Replace null-bytes in Task with space, making sure individual elements are quotation-enclosed
                        taskSplit = task.task.split("\x00")
                        for index,taskSplitIndividual in enumerate(taskSplit):
                            if " " in taskSplitIndividual:
                                taskSplit[index] = "\"" + taskSplitIndividual + "\""
                        taskProcessed = " ".join(taskSplit)

                        # Prepare notification for this Task
                        notificationMessage += f"- Agent {task.agentId} [Task {task.id}]$ {taskProcessed}\n{task.output}\nCompleted at {convertUnixTimeToHumanReadable(task.outputAt)}\n\n"
                    socketClient.sendall(f"SUCCESS: New tasks output\n\n{notificationMessage}".encode("utf-8"))  
                
                # Sleep before checking for new messages to send
                sleep(10.0)

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Administration
        return False
