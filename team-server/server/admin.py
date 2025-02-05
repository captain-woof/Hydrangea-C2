import bcrypt
from database.database import HydrangeaDatabase
from .socket_custom import SocketCustom

# Constants
ADMIN_COMMANDS_PREFIX = (
    "newuser",
    "editusername",
    "editpassword",
    "editrole",
    "deluser"
)

# Hash password
def hashPassword(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Handles Administrative command and communicates result to client; returns False if the input command is not an Admin command
def handleAdminCommand(db: HydrangeaDatabase, socketClient: SocketCustom, user, userInput: str):
    # If command is for Administration, handle here
    if userInput.startswith(ADMIN_COMMANDS_PREFIX):
        # Verify user's role; if not admin, do below
        if user.role != "admin":
            socketClient.sendall(b"ERROR: You are not an admin")

        # Else if admin, do below
        else:
            # Split command
            userInputSplit = userInput.split(" ")

            # New user
            if userInput.startswith("newuser"): # newuser USERNAME PASSWORD ROLE
                if userInputSplit[3] not in ["admin", "operator", "observer"]:
                    socketClient.sendall(b"ERROR: Incorrect role")
                else:    
                    if db.createUser(username=userInputSplit[1], passwordHash=hashPassword(userInputSplit[2]), role=userInputSplit[3]):
                        socketClient.sendall(f"SUCCESS: User {userInputSplit[1]}({userInputSplit[3]}) created successfully".encode("utf-8"))
                    else:
                        socketClient.sendall(f"ERROR: Failed to create user '{userInputSplit[1]}'".encode("utf-8"))

            # Edit user's username
            elif userInput.startswith("editusername"): # editusername USERNAME NEW_USERNAME
                if db.changeUserUsername(username=userInputSplit[1], usernameNew=userInputSplit[2]):
                    socketClient.sendall(f"SUCCESS: User {userInputSplit[1]}'s new username set to '{userInputSplit[2]}'".encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to change user {userInputSplit[1]}'s new username to '{userInputSplit[2]}'".encode("utf-8"))

            # Edit user's password
            elif userInput.startswith("editpassword"): # editpassword USERNAME NEW_PASSWORD
                if db.changeUserPassword(username=userInputSplit[1], passwordHashNew=userInputSplit[2]):
                    socketClient.sendall(f"SUCCESS: User {userInputSplit[1]}'s new password set".encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to change user {userInputSplit[1]}'s new password".encode("utf-8"))

            # Edit user's role
            elif userInput.startswith("editrole"): # editrole USERNAME NEW_ROLE
                if userInputSplit[2] not in ["admin", "operator", "observer"]:
                    socketClient.sendall(b"ERROR: Incorrect role")
                else:
                    if db.changeUserRole(username=userInputSplit[1], roleNew=userInputSplit[2]):
                        socketClient.sendall(f"SUCCESS: User {userInputSplit[1]}'s new role set to '{userInputSplit[2]}'".encode("utf-8"))
                    else:
                        socketClient.sendall(f"ERROR: Failed to change user {userInputSplit[1]}'s new role to '{userInputSplit[2]}'".encode("utf-8"))

            # Delete user
            elif userInput.startswith("deluser"): # deluser USERNAME
                if db.deleteUser(username=userInputSplit[1]):
                    socketClient.sendall(f"SUCCESS: User '{userInputSplit[1]}' deleted".encode("utf-8"))
                else:
                    socketClient.sendall(f"ERROR: Failed to delete user '{userInputSplit[1]}'".encode("utf-8"))

        # Return true because command has been handled        
        return True
    else:
        # Return false if command is not for Administration
        return False