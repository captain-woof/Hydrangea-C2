from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from database.database import HydrangeaDatabase
import bcrypt

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
    authResults = db.getUserByUsername(username=username).first()
    if authResults is None:
        await websocket.send_text("ERROR: User does not exist / incorrect auth")
        return await websocket.close()

    ### Validate password
    passwordInDb = authResults.password
    resultPasswordHashCheck = bcrypt.checkpw(password.encode("utf-8"), passwordInDb.encode("utf-8"))
    if not resultPasswordHashCheck:
        await websocket.send_text("ERROR: User does not exist / incorrect auth")
        return await websocket.close()

    # Start tasker loop
    await websocket.send_text(f"SUCCESS: Logged in as {username}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print(f"INFO: User '{username}' quit")
