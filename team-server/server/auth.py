from database.database import HydrangeaDatabase
from .socket_custom import SocketCustom
import bcrypt

# Handles authentication
def handleAuth(db: HydrangeaDatabase, socketClient: SocketCustom):
    # Authentication
    authData = socketClient.recvall()
    username, password = map(lambda x: x.decode("utf-8"), authData.split(b"\x00"))

    ## Validate username
    user = db.getUserByUsername(username=username)
    if user is None:
        socketClient.sendall(b"ERROR: User does not exist / incorrect auth")
        socketClient.close()
        return None
    
    ## Validate password
    passwordInDb = user.password
    resultPasswordHashCheck = bcrypt.checkpw(password.encode("utf-8"), passwordInDb.encode("utf-8"))
    if not resultPasswordHashCheck:
        socketClient.sendall(b"ERROR: User does not exist / incorrect auth")
        socketClient.close()
        return None
    
    print(f"SUCCESS: User '{username}' logged in")
    socketClient.sendall(b"SUCCESS: Logged in")

    return user
