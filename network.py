import socket
import pickle
import struct

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "172.24.240.1"
        self.port = 5555
        self.addr = (self.server, self.port)


    def connect(self, name):

        # connects to server

        self.client.connect(self.addr)
        self.send_data(name)
        client_id = self.receive_data()
        return client_id

    
    def disconnect(self):

        #disconnects from server

        self.client.close()

    def send_data(self, data):

        # print("sending data: ", data)
        serialized_data = pickle.dumps(data)
        self.client.send(struct.pack('i', len(serialized_data)))
        self.client.send(serialized_data)

    def receive_data(self):
        data_size = struct.unpack('i', self.client.recv(4))[0]
        received = self.client.recv(data_size)
        data = pickle.loads(received)

        # print("received data: ", data)
        return data
