from argparse import ArgumentParser
from server import TeamServer

if __name__ == "__main__":
    # Define command line args
    parser = ArgumentParser(description="Starts Hydrangea C2 team server")
    parser.add_argument("-H", "--host", action="store", default="127.0.0.1", help="Hydrangea C2's team server hostname/IP; default: 127.0.0.1")
    parser.add_argument("-P", "--port", action="store", type=int, default=6060, help="Hydrangea C2's team server port; default: 6060")
    args = parser.parse_args()

    host = args.host
    port = args.port

    # Start team server
    try:
        teamServer = TeamServer(host=host, port=port, maxConns=20)
        teamServer.start()
    except KeyboardInterrupt:
        print("Quitting team server...")
        teamServer.stop()
    except Exception:
        teamServer.stop()