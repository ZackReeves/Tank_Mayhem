#imports
import socket
import pygame
import time
import random
import pickle
import struct
import math
from utils import rotate_center, scale_image
from _thread import *

#setup socket
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#constants
PORT = 12000

TANK = scale_image(pygame.image.load("img/tank.png"), 0.19, 0.19)
BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.20, 0.10)
BOXES = [scale_image(pygame.image.load("img/logs.png"), 0.66, 0.81), scale_image(pygame.image.load("img/barrel.png"), 0.66, 0.81), scale_image(pygame.image.load("img/tree.png"), 0.66, 0.81), scale_image(pygame.image.load("img/snowman.png"), 0.66, 0.81)]

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800

GRID_SIZE = 25

TANK_W = TANK.get_width()
TANK_H = TANK.get_height()

BULLET_W = BULLET.get_width()
BULLET_H = BULLET.get_height()

BOX_W = []
BOX_H = []

for BOX in BOXES:

    BOX_W.append(BOX.get_width())
    BOX_H.append(BOX.get_height())

MAX_VEL = 2

HOST_NAME = socket.gethostname()
SERVER_IP = '0.0.0.0' #socket.gethostbyname(HOST_NAME)

#connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()

print(f"[SERVER] Server started with ip {SERVER_IP}")

#dynamic variable
players = {}
boxes = []
new_bullets = {}
connections = 0
_id = 0
start = False


#functions

def get_start_position(players):

    stop = False

    while not stop:

        stop = True

        x = random.randrange(0, SCREEN_WIDTH-TANK_W)
        y = random.randrange(0, SCREEN_HEIGHT-TANK_H)
        angle = random.randrange(0, 360)

        rotated_tank, tank_rect = rotate_center(TANK, (x, y), angle)
        tank_mask = pygame.mask.from_surface(rotated_tank)

        for box in boxes:

            box_mask = pygame.mask.from_surface(BOXES[box[2]])

            offset = (int(box[0] - tank_rect[0]), int(box[1] - tank_rect[1]))

            no_bits = tank_mask.overlap_area(box_mask, offset)

            if no_bits != 0:
                stop = False
    
    
    return (x,y,angle)

def create_boxes(boxes, n):
    for i in range(n):
        while True:
            stop = True
            x = random.randrange(0, SCREEN_WIDTH / (2*GRID_SIZE)) * random.choice((GRID_SIZE, 2 * GRID_SIZE))
            y = random.randrange(0, SCREEN_HEIGHT / (2*GRID_SIZE)) * random.choice((GRID_SIZE, 2 * GRID_SIZE))
            image_id = random.randrange(0,len(BOXES))
            for player in players:
                p = players[player]
                if p["x"] <= x + BOX_W[image_id] and p["x"] + TANK_W >= x and p["y"] <= y + BOX_H[image_id] and p["y"] + TANK_H >= y:
                    stop = False
            
            if stop:
                break
        
        boxes.append((x, y, image_id))
    
    boxes.sort(key=lambda x: x[1])

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

    #print("sending data: ", data)
    #print(len(serialized_data))

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

    global connections, players, boxes, new_bullets, start

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

    setup = boxes, players, start
    send_data(conn, setup)

    while True:

        try:
            command, data, del_box, new_bullet = receive_data(conn)              
            
            if not data:
                break

            if command == "":

                if del_box != ():
                    try:
                        boxes.pop(boxes.index(del_box))
                    except:
                        pass
                
                new_bullets[current_id] = new_bullet

                if len(boxes) < 10:
                    print("[GAME] Generating more boxes")
                    create_boxes(boxes, random.randrange(5, 10))
                
            
            elif command == "ready":
                if len(players) > 1:
                    ready_up(players, connections)

            else:
                print("[WARNING] No command received")

            players[current_id] = data
            
            data = boxes, players, new_bullets, start
            
            send_data(conn, data)

        except Exception as e:
            print(e)
            break

        time.sleep(0.001)
    
    print("[DISCONNECT] Name:", name, ", Client Id:", current_id, "disconnected")

    connections -= 1
    try:
        del players[current_id]
    except:
        pass

    if connections == 0:
        print("[SERVER] No connections, resetting")
        players = {}
        boxes = []
        bullets = []
        connections = 0
        _id = 0
        start = False

        create_boxes(boxes, random.randint(10, 20))


    conn.close()



#MAINLOOP

#setup level with boxes
create_boxes(boxes, random.randint(10, 20))
print("LENGTH OF BOXES:", len(boxes))

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
