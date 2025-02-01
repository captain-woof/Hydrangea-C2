import asyncio
import websockets
from argparse import ArgumentParser

# Define command line args
parser = ArgumentParser(description="Starts Hydrangea C2 client")
parser.add_argument("-H", "--host", action="store", default="127.0.0.1", help="Hydrangea C2's team server hostname/IP; default: 127.0.0.1")
parser.add_argument("-P", "--port", action="store", default="6060", help="Hydrangea C2's team server port; default: 6060")
args = parser.parse_args()

# Client entrypoint
async def runClient():
    try:
        async with websockets.connect(f"ws://{args.host}:{args.port}/ws") as websocket:
            # Authenticate
            username = input("Username: ")
            password = input("Password: ")
            await websocket.send(username.encode("utf-8") + b"\x00" + password.encode("utf-8"))
            authResponse = await websocket.recv()
            print(authResponse)
            if authResponse.startswith("ERROR:"):
                return

            # Start client loop
            while True:
                await websocket.send(input(f"Tasker ({args.host}:{args.port}) > "))

                response = await websocket.recv()
                print(response)

    except ConnectionRefusedError:
        print("ERROR: Failed to connect with server. Is server running?")

    except KeyboardInterrupt:
        print("SUCCESS: Quit")

# Run client
if __name__ == "__main__":
    asyncio.run(runClient())