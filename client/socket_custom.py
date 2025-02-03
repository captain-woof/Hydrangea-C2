import socket
import struct

class SocketCustom():
    socketToWrap: socket.socket

    def __init__(self, socketToWrap: socket.socket = None):
        self.socketToWrap = socketToWrap if socketToWrap is not None else socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Sends all of the input data
    def sendall(self, data):
        # Prefix each message with a 4-byte length (network byte order)
        dataToSend = struct.pack('>I', len(data)) + data
        return self.socketToWrap.sendall(dataToSend)
    
    # Receives all data
    def recvall(self):
        # Read message length and unpack it into an integer
        lenDataRaw = self.recv(4)
        if not lenDataRaw:
            return None
        lenData = struct.unpack('>I', lenDataRaw)[0]
        # Read the message data
        return self.recv(lenData)

    # Receives N bytes of data
    def recv(self, bufsize: int):
        data = bytearray()
        while len(data) < bufsize:
            packet = self.socketToWrap.recv(bufsize - len(data))
            if not packet:
                break
            data.extend(packet)
        return data
    
    # Connect
    def connect(self, address: tuple):
        return self.socketToWrap.connect(address)
    
    # Bind
    def bind(self, address: tuple):
        return self.socketToWrap.bind(address)
    
    # Listen
    def listen(self):
        return self.socketToWrap.listen()
    
    # Accepts client socket
    def accept(self):
        socketClient, addrClient = self.socketToWrap.accept()
        return (SocketCustom(socketClient), addrClient)
    
    # Close
    def close(self):
        return self.socketToWrap.close()

