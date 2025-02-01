import asyncio
import websockets
from argparse import ArgumentParser
import help


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
                userInput = input(f"{username}@Tasker ({args.host}:{args.port}) > ")

                # Handle admin functions
                if userInput == "context admin":
                    while True:
                        userInput = input(f"{username}@Tasker ({args.host}:{args.port}) > Admin > ")

                        # Print 'context admin' Help
                        if userInput == "help":
                            print(help.HELP_CONTEXT_ADMIN)

                        # Go back from 'context admin'
                        elif userInput in ["back", "quit", "exit"]:
                            break

                        # Send command to server
                        else:
                            await websocket.send(userInput)
                            response = await websocket.recv()
                            print(response)

                # Handle quit to exit client
                elif userInput in ["quit", "exit"]:
                    await websocket.send("quit")
                    response = await websocket.recv()
                    print(response)
                    break

                # Print 'main menu' help
                elif userInput == "help":
                    print(help.HELP_MAIN_MENU)

                # Handle listener function TODO

                # Handle payload function TODO

                # Wrong command
                else:
                    print("ERROR: Wrong command")

    except ConnectionRefusedError:
        print("ERROR: Failed to connect with server. Is server running?")

    except KeyboardInterrupt:
        print("SUCCESS: Quit")

# Run client
if __name__ == "__main__":
    asyncio.run(runClient())