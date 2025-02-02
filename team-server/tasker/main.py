from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from database.database import HydrangeaDatabase
import bcrypt
import tasker.admin as adminFunc

app = FastAPI(
    title="Hydrangea C2 - Tasker",
    description="Connect to this over WebSocket to interact with team server",
    debug=False
)

@app.websocket("/ws")
async def startCommunication(websocket: WebSocket):
    # Start communication with client
    await websocket.accept()

    # Get database manager for this session
    db = HydrangeaDatabase()

    ## Authentication
    authData = await websocket.receive_bytes()
    username, password = map(lambda x: x.decode("utf-8"), authData.split(b"\x00"))

    ### Validate username
    user = adminFunc.getUserByUsername(db=db, username=username).first()
    if user is None:
        await websocket.send_text("ERROR: User does not exist / incorrect auth")
        return await websocket.close()

    ### Validate password
    passwordInDb = user.password
    resultPasswordHashCheck = bcrypt.checkpw(password.encode("utf-8"), passwordInDb.encode("utf-8"))
    if not resultPasswordHashCheck:
        await websocket.send_text("ERROR: User does not exist / incorrect auth")
        return await websocket.close()

    # Start tasker loop
    await websocket.send_text(f"SUCCESS: Logged in as {username}")
    try:
        while True:
            # Receive command from user
            userInput = await websocket.receive_text()
            userInputSplit = userInput.split(" ")
            
            # Perform command

            ## Quit
            if userInput == "quit": # User wants to quit
                await websocket.send_text(f"SUCCESS: Bye {username}")
                await websocket.close()
                return

            ## Administrator commands
            if userInput.startswith("newuser"): # newuser USERNAME PASSWORD ROLE
                if user.role != "admin":
                    await websocket.send_text(f"ERROR: You are not an admin")
                    continue
                result = adminFunc.createUser(db=db, username=userInputSplit[1], password=userInputSplit[2], role=userInputSplit[3])
                if result:
                    await websocket.send_text(f"SUCCESS: User {userInputSplit[1]}({userInputSplit[3]}) created successfully")
                else:
                    await websocket.send_text(f"ERROR: User {userInputSplit[1]}({userInputSplit[3]}) could not be created")
            elif userInput.startswith("editusername"): # editusername USERNAME NEW_USERNAME
                if user.role != "admin":
                    await websocket.send_text(f"ERROR: You are not an admin")
                    continue
                result = adminFunc.editUser(db=db, username=userInputSplit[1], changeWhat="username", newValue=userInputSplit[2])
                if result:
                    await websocket.send_text(f"SUCCESS: User {userInputSplit[1]}'s new username set to '{userInputSplit[2]}'")
                else:
                    await websocket.send_text(f"ERROR: Failed to change user {userInputSplit[1]}'s new username to '{userInputSplit[2]}'")
            elif userInput.startswith("editpassword"): # editpassword USERNAME NEW_PASSWORD
                if user.role != "admin":
                    await websocket.send_text(f"ERROR: You are not an admin")
                    continue
                result = adminFunc.editUser(db=db, username=userInputSplit[1], changeWhat="password", newValue=userInputSplit[2])
                if result:
                    await websocket.send_text(f"SUCCESS: User {userInputSplit[1]}'s new password set")
                else:
                    await websocket.send_text(f"ERROR: Failed to change user {userInputSplit[1]}'s new password")
            elif userInput.startswith("editrole"): # editrole USERNAME NEW_ROLE
                if user.role != "admin":
                    await websocket.send_text(f"ERROR: You are not an admin")
                    continue
                result = adminFunc.editUser(db=db, username=userInputSplit[1], changeWhat="role", newValue=userInputSplit[2])
                if result:
                    await websocket.send_text(f"SUCCESS: User {userInputSplit[1]}'s new role set to '{userInputSplit[2]}'")
                else:
                    await websocket.send_text(f"ERROR: Failed to change user {userInputSplit[1]}'s new role to '{userInputSplit[2]}'")
            elif userInput.startswith("deluser"): # deluser USERNAME
                if user.role != "admin":
                    await websocket.send_text(f"ERROR: You are not an admin")
                    continue
                result = adminFunc.deleteUser(db=db, username=userInputSplit[1])
                if result:
                    await websocket.send_text(f"SUCCESS: User '{userInputSplit[1]}' deleted")
                else:
                    await websocket.send_text(f"ERROR: Failed to delete user '{userInputSplit[1]}'")


            ## TODO commands

            else: # error
                await websocket.send_text("ERROR: Wrong command")

    except WebSocketDisconnect:
        print(f"INFO: User '{username}' quit")
