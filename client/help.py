"""
This file contains help menu for client
"""

HELP_MAIN_MENU = """
> MAIN CONTEXT

COMMAND       : PURPOSE
-----------------------
context admin : Switches to administration context to manage team server

quit/exit     : Quits client
"""

HELP_CONTEXT_ADMIN = """
> ADMIN CONTEXT

COMMAND                            : PURPOSE
--------------------------------------------

newuser USERNAME PASSWORD ROLE     : Creates a new user; usernames are unique; roles can be "admin", "operator", "observer"
editusername USERNAME NEW_USERNAME : Edits an existing user's username; usernames are unique
editpassword USERNAME NEW_PASSWORD : Edits an existing user's password
editrole USERNAME NEW_ROLE         : Edits an existing user's role; roles can be "admin", "operator", "observer"
deluser USERNAME                   : Deletes an existing user; this is permanent

quit/exit/back                     : Go back to main context
"""

HELP_CONTEXT_LISTENER = """

"""

HELP_CONTEXT_PAYLOAD = """

"""