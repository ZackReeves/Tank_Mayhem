import socket
import pickle
import struct

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "18.234.140.248"
        self.port = 12000
        self.addr = (self.server, self.port)


    def connect(self, name):

        # connects to server
        try:
            self.client.connect(self.addr)
            self.send_data(name)
            client_id = self.receive_data()
        except:
            print("failed to connect")
        
        return client_id

    
    def disconnect(self):

        #disconnects from server

        self.client.close()

    def send_data(self, data):

        #print(data)

        #print("sending data: ", data)
        serialized_data = pickle.dumps(data)
        self.client.send(struct.pack('i', len(serialized_data)))
        self.client.send(serialized_data)

    def receive_data(self):
        data_size = struct.unpack('i', self.client.recv(4))[0]
        #print(data_size)

        received = self.client.recv(data_size)
        #print(len(received))

        data = pickle.loads(received) #!!!!

        #print("received data: ", data)
        return data
