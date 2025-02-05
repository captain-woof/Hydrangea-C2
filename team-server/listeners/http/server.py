from flask import Flask
from database.database import HydrangeaDatabase

# Database
db = HydrangeaDatabase()

# Flask WSGI app
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


"""
AGENT CHECK IN
checkin agent_id

TASKS
base64(
taskid-base64(task)
taskid-base64(task)
)

TASKS OUTPUT
base64(
taskid-base64(output)
taskid-base64(output)
)
"""