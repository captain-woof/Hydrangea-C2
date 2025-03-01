from flask import Flask, render_template, abort, request
from server.database import HydrangeaDatabase
import json
import os
import base64
from listeners.base import handleAgentCommunication

# Database
db = HydrangeaDatabase()

# Flask WSGI app
app = Flask(__name__)

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
    agentMessageB64 = request.headers.get("HTTP-X-AUTH")
    if agentMessageB64 is not None:
        print("Message from agent (base64)", agentMessageB64)

        agentReply = handleAgentCommunication(
            db=db,
            agentMessageBytes=base64.b64decode(agentMessageB64.encode("utf-8"))
        )
        agentReplyEncoded = base64.b64encode(agentReply).decode("utf-8")

        # Insert message to agent in base64 data for image
        post['hero_image_base64'] = f"data:image/svg+xml;base64,{agentReplyEncoded if len(agentReplyEncoded) != 0 else ""}"
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
