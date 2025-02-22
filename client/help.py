from utils import dictArrayToTable

"""
This file contains help menu for client
"""

HELP_MAIN_MENU = dictArrayToTable([
    {"COMMAND": "context admin", "ARGS": "", "DESCRIPTION": "Switches to administration context to manage team server"},
    {"COMMAND": "context listener", "ARGS": "", "DESCRIPTION": "Switches to listeners context to control and query listeners"},
    {"COMMAND": "context agent", "ARGS": "", "DESCRIPTION": "Switches to agent context to control agents"},
    {"COMMAND": "quit/exit", "ARGS": "", "DESCRIPTION": "Disconnects from server and quits client"}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])

HELP_CONTEXT_ADMIN = dictArrayToTable([
    {"COMMAND": "cleartable", "ARGS": "TABLE_NAME", "DESCRIPTION": "Clears table (available: users, tasks, agents)"},
    {"COMMAND": "newuser", "ARGS": "USERNAME PASSWORD ROLE", "DESCRIPTION": "Creates a new user; usernames are unique; roles can be admin, operator, observer"},
    {"COMMAND": "editusername", "ARGS": "USERNAME NEW_USERNAME", "DESCRIPTION": "Edits an existing user's username; usernames are unique"},
    {"COMMAND": "editpassword", "ARGS": "USERNAME NEW_PASSWORD", "DESCRIPTION": "Edits an existing user's password"},
    {"COMMAND": "editrole", "ARGS": "USERNAME NEW_ROLE", "DESCRIPTION": "Edits an existing user's role; roles can be admin, operator, observer"},
    {"COMMAND": "deluser", "ARGS": "USERNAME", "DESCRIPTION": "Deletes an existing user; this is permanent"},
    {"COMMAND": "quit/exit/back", "ARGS": "", "DESCRIPTION": "Go back to main context"}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])

HELP_CONTEXT_LISTENER = dictArrayToTable([
    {"COMMAND": "listenernew", "ARGS": "TYPE HOST PORT", "DESCRIPTION": "Creates a new listener on Team server; TYPE can be 'http'"},
    {"COMMAND": "listenersget", "ARGS": "", "DESCRIPTION": "Get all running listeners' IDs"},
    {"COMMAND": "listenerdel", "ARGS": "LISTENER_ID", "DESCRIPTION": "Stops a running listener"},
    {"COMMAND": "quit/exit/back", "ARGS": "", "DESCRIPTION": "Go back to main context"}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])

HELP_CONTEXT_AGENT = dictArrayToTable([
    {"COMMAND": "agentsget", "ARGS": "", "DESCRIPTION": "Gets all agents"},
    {"COMMAND": "agentinteract", "ARGS": "AGENT_ID", "DESCRIPTION": "Interact with agent"},
    {"COMMAND": "agentstasksget", "ARGS": "", "DESCRIPTION": "Get all tasks of all agents"},
    {"COMMAND": "quit/exit/back", "ARGS": "", "DESCRIPTION": "Go back to main context"}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])

HELP_CONTEXT_AGENT_CAPABILITIES = dictArrayToTable([
    {"COMMAND": "tasksget", "ARGS": "", "DESCRIPTION": "Get all tasks of the agent"},
    {"COMMAND": "messagebox", "ARGS": "TITLE BODY", "DESCRIPTION": "Show and focus on messagebox on target"},
    {"COMMAND": "exit", "ARGS": "", "DESCRIPTION": "Agent exits on target after finishing up on remaining tasks"},
    {"COMMAND": "quit/back", "ARGS": "", "DESCRIPTION": "Go back to main context"}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])

HELP_CONTEXT_PAYLOAD = dictArrayToTable([
    {"COMMAND": "", "ARGS": "", "DESCRIPTION": ""},
    {"COMMAND": "", "ARGS": "", "DESCRIPTION": ""},
    {"COMMAND": "", "ARGS": "", "DESCRIPTION": ""},
    {"COMMAND": "", "ARGS": "", "DESCRIPTION": ""}
], headerOrderList=["COMMAND", "ARGS", "DESCRIPTION"])
