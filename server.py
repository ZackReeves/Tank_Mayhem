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

BULLET_SIZE = (2,6)

W, H = 800, 800

TANK_W = 30
TANK_H = 30

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
    for i in range(2*n):
        while True:
            stop = True
            x = random.randrange(1, 30)*random.choice((25, 50))
            y = random.randrange(1, 30)*25
            for player in players:
                p = players[player]
                if p["x"] <= x + BOX_SIZE & p["x"] >= x & p["y"] <= y + BOX_SIZE & p["y"] >= y:
                    stop = False
            
            if stop:
                break
        
        boxes.append((x, y))
    
    boxes.sort(key=lambda x: x[1])

def create_bullet(player):
    max_vel = 2
    x = player["x"] + 2
    y = player["y"]
    angle = player["angle"]
    vel = (player["velocity"] + 2*max_vel) / 2 # normalises to 0.5 max_vel < vel < 1.5 max_vel

    bullets.append((x, y, angle, vel))

def check_collisions(player, old_x, old_y):
    new_x = player["x"]
    new_y = player["y"]
    
    if new_x < 0:
        new_x = 0
    elif new_x > W-TANK_W:
        new_x = W-TANK_W

    if new_y < 0:
        new_y = 0
    elif new_y > H-TANK_H:
        new_y = H-TANK_H

    for box in boxes:
        collide = False

        if new_y + TANK_H > box[1] and new_y < box[1] + BOX_SIZE:
            if new_x + TANK_W > box[0] and new_x < box[0] + BOX_SIZE:
                collide = True

        if old_y + TANK_H > box[1] and old_y < box[1] + BOX_SIZE and collide:
            if old_x > box[0]:
                new_x = box[0] + BOX_SIZE

            elif old_x < box[0]:
                new_x = box[0] - TANK_W
        
        if old_x + TANK_W > box[0] and old_x < box[0] + BOX_SIZE and collide:
                if old_y < box[1]:
                    new_y = box[1] - TANK_H

                elif old_y > box[1]:
                    new_y = box[1] + BOX_SIZE

    player["x"] = new_x
    player["y"] = new_y
    

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

    #print("received data: ", data)

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
            
            if not data:
                break

            if command == "":

                if start:

                    check_collisions(data, players[current_id]["x"], players[current_id]["y"])

                    #check hits


                    
                    #if players[current_id]["fired"]:
                    #    create_bullet()
                    
                    #move bullets()
                
                players[current_id] = data
                    
                
                if len(boxes) < 25:
                    create_boxes(boxes, random.randrange(15, 25))
                    print("[GAME] Generating more boxes")
                
            
            elif command == "ready":
                players[current_id] = data
                ready_up(players, connections)

            else:
                players[current_id] = data
                print("[WARNING] No command received")
            
            data = boxes, players, bullets, start
            
            send_data(conn, data)

        except Exception as e:
            print(e)
            break

        time.sleep(0.001)
    
    print("[DISCONNECT] Name:", name, ", Client Id:", current_id, "disconnected")

    connections -= 1
    if connections == 0:
        start = False
    del players[current_id]
    conn.close()



#MAINLOOP

#setup level with boxes
create_boxes(boxes, random.randrange(50, 70))

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
    