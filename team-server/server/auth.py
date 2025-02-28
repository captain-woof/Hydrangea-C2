from .database import HydrangeaDatabase
from .socket_custom import SocketCustom
import bcrypt

# Handles authentication
def handleAuth(db: HydrangeaDatabase, socketClient: SocketCustom, addrClient: tuple):
    # Authentication
    authData = socketClient.recvall()
    username, password = map(lambda x: x.decode("utf-8"), authData.split(b"\x00"))

    ## Validate username
    user = db.getUserByUsername(username=username)
    if user is None:
        socketClient.sendall(b"ERROR: User does not exist / incorrect auth")
        socketClient.close()
        return (None, None)
    
    ## Validate password
    passwordInDb = user.password
    resultPasswordHashCheck = bcrypt.checkpw(password.encode("utf-8"), passwordInDb.encode("utf-8"))
    if not resultPasswordHashCheck:
        socketClient.sendall(b"ERROR: User does not exist / incorrect auth")
        socketClient.close()
        return (None, None)
    
    # Prepare client ID and send in response
    clientId = f"{username}-{addrClient[0]}:{addrClient[1]}"
    socketClient.sendall(f"SUCCESS: Logged in; clientId = '{clientId}'".encode("utf-8"))
    
    print(f"SUCCESS: User '{username}' logged in")

    return (user, clientId)
