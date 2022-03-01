#imports
import socket
import time
import random
import pickle
import struct
from _thread import *

server = "192.168.0.18" 
PORT = 5555

#setup socket
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#constants
PORT = 5555

BOX_SIZE = 25

W, H = 800, 800

HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

#connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()

print(f"[SERVER] Server started with local ip {SERVER_IP}")

#dynamic variable
players = {}
boxes = []
bullets = []
connections = 0
_id = 0
start = False


#functions
    
#pos = [(150,60,randangle()), (650,740,randangle()), (650,60,randangle()), (150,740,randangle()), (400,740,randangle()), (400,60,randangle())]

def get_start_position(players):

    x = random.randrange(100, W-100)
    y = random.randrange(60, H-60)
    angle = random.randrange(0, 360)

    return (x,y,angle)
    

def create_boxes(boxes, n):
    for i in range(n):
        while True:
            stop = True
            x = random.randrange(150, 650)
            y = random.randrange(60, 740)
            for player in players:
                p = players[player]
                if p["x"] <= x + BOX_SIZE & p["x"] >= x & p["y"] <= y + BOX_SIZE & p["y"] >= y:
                    stop = False
            
            if stop:
                break
        
        boxes.append((x, y))

def ready_up(players, connections):

    global start

    readied = 0
    for player in players:
        p = players[player]
        if p["ready"]:
            readied += 1
    
    if readied == connections:
        start = True

def send_data(conn, data):

    # print("sending data: ", data)

    serialized_data = pickle.dumps(data)
    conn.send(struct.pack('i', len(serialized_data)))
    conn.send(serialized_data)


def receive_data(conn):
    data_size = struct.unpack('i', conn.recv(4))[0]
    received = conn.recv(data_size)
    data = pickle.loads(received)

    print("received data: ", data)

    return data

def threaded_client(conn, _id):

    global connections, players, boxes, bullets, start

    current_id = _id

    # receive name
    name = receive_data(conn)
    print("[LOG]", name, "connected to the server.")

    # setup player properties
    x, y, angle = get_start_position(players)
    fired = False
    vel = 0
    health = 10
    ready = False    
    
    players[current_id] = {"x":x, "y":y, "angle":angle, "fired":fired, "velocity":vel, "health":health, "name":name, "ready":ready} 


    send_data(conn, current_id)

    setup = boxes, players, bullets, start
    send_data(conn, setup)

    while True:

        #if start:
            #condition for endgame

        try:
            command, data = receive_data(conn)

            players[current_id] = data
            
            if not data:
                break

            if command == "":
                
                #if fired:
                    #create bullet


                #if start:
                    #move bullets()
                    #check_box_hit()
                    #check_player_hit()
                    
                
                if len(boxes) < 25:
                    create_boxes(boxes, random.randrange(15, 25))
                    print("[GAME] Generating more boxes")
                
                data = boxes, players, bullets, start
            
            elif command == "ready":
                ready_up(players, connections)

            else:
                print("[WARNING] No command received")

                data = boxes, players, bullets, start
            
            data = boxes, players, bullets, start
            
            send_data(conn, data)

        except Exception as e:
            print(e)
            break

        time.sleep(0.001)
    
    print("[DISCONNECT] Name:", name, ", Client Id:", current_id, "disconnected")

    connections -= 1
    del players[current_id]
    conn.close()



#MAINLOOP

#setup level with boxes
create_boxes(boxes, random.randrange(50, 100))

print("[GAME] Setting up level")
print("[SERVER] Waiting for a connection, Server Started")

#loop to accept connections
while True:

    conn, addr = S.accept()

    if connections < 6:
        print("Connected to:", addr)

        connections += 1
        start_new_thread(threaded_client, (conn, _id))
        _id += 1
    
    else:
        conn.close()



print("[SERVER] Server offline")
    