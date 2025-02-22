"""
This file contains help menu for client
"""

HELP_MAIN_MENU = """
> MAIN CONTEXT

COMMAND          : PURPOSE
--------------------------
context admin    : Switches to administration context to manage team server
context listener : Switches to listeners context to control and query listeners
context agent    : Switches to agent context to control agents

quit/exit     : Quits client
"""

HELP_CONTEXT_ADMIN = """
> ADMIN CONTEXT

COMMAND                            : PURPOSE
--------------------------------------------

cleartable TABLE_NAME              : Clears table (available: users, tasks, agents)
newuser USERNAME PASSWORD ROLE     : Creates a new user; usernames are unique; roles can be "admin", "operator", "observer"
editusername USERNAME NEW_USERNAME : Edits an existing user's username; usernames are unique
editpassword USERNAME NEW_PASSWORD : Edits an existing user's password
editrole USERNAME NEW_ROLE         : Edits an existing user's role; roles can be "admin", "operator", "observer"
deluser USERNAME                   : Deletes an existing user; this is permanent

quit/exit/back                     : Go back to main context
"""

HELP_CONTEXT_LISTENER = """
COMMAND                    : PURPOSE
------------------------------------

listenernew TYPE HOST PORT : Creates a new listener; TYPE can be 'http'
listenersget               : Get all running listeners
listenerdel LISTENER_ID    : Stops a running listener
"""

HELP_CONTEXT_AGENT = """
COMMAND                : PURPOSE
--------------------------------

agentsget              : Gets all agents
agentinteract AGENT_ID : Interact with agent
agentstasksget         : Get all tasks of all agents
"""

HELP_CONTEXT_AGENT_CAPABILITIES = """
COMMAND                : PURPOSE
--------------------------------

tasksget               : Get all tasks of the agent
messagebox TITLE BODY  : Show a messagebox on target
exit                   : Agent exits on target
"""

HELP_CONTEXT_PAYLOAD = """

"""