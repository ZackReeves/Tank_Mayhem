#imports
import socket
from tkinter.tix import MAX
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

W, H = 800, 800

GRID_SIZE = 25

BOX_W = []
BOX_H = []

for BOX in BOXES:

    BOX_W.append(BOX.get_width())
    BOX_H.append(BOX.get_height())

BULLET_W = BULLET.get_width()
BULLET_H = BULLET.get_height()

TANK_W = TANK.get_width()
TANK_H = TANK.get_height()

MAX_VEL = 2

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

print(f"[SERVER] Server started with ip {SERVER_IP}")

#dynamic variable
players = {}
boxes = []
bullets = []
connections = 0
_id = 0
start = False


#functions

def get_start_position(players):

    stop = False

    while not stop:

        stop = True

        x = random.randrange(0, W-TANK_W)
        y = random.randrange(0, H-TANK_H)
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
            x = random.randrange(0, W / (2*GRID_SIZE)) * random.choice((GRID_SIZE, 2 * GRID_SIZE))
            y = random.randrange(0, H / (2*GRID_SIZE)) * random.choice((GRID_SIZE, 2 * GRID_SIZE))
            image_id = random.randrange(0,len(BOXES))
            for player in players:
                p = players[player]
                if p["x"] <= x + BOX_W[image_id] and p["x"] + TANK_W >= x and p["y"] <= y + BOX_H[image_id] and p["y"] + TANK_H >= y:
                    stop = False
            
            if stop:
                break
        
        boxes.append((x, y, image_id))
    
    boxes.sort(key=lambda x: x[1])

def create_bullet(player):

    angle = player["angle"]

    tank_rect = pygame.Rect(player["x"], player["y"], TANK_W, TANK_H)
    
    bullet_rect = pygame.Rect(0, 0, BULLET_W, BULLET_H)

    dist = 0.5*TANK_H + BULLET_H
    radians = math.radians(angle)

    bullet_rect.centerx = tank_rect.centerx - dist * math.sin(radians)
    bullet_rect.centery = tank_rect.centery - dist * math.cos(radians)


    vel = 0.375 * (player["velocity"] + MAX_VEL) + MAX_VEL # normalises to 1 max_vel < vel < 1.5 max_vel

    bullets.append((bullet_rect.topleft[0], bullet_rect.topleft[1], angle, vel))

def move_bullets():

    for bullet in bullets: # bullets = [(x, y, a, v), (), ()]

        i = bullets.index(bullet)

        radians = math.radians(bullet[2])

        vertical = math.cos(radians) * bullet[3]
        horizontal = math.sin(radians) * bullet[3]
        
        new_x = bullet[0] - horizontal
        new_y = bullet[1] - vertical

        bullets[i] = (new_x, new_y, bullet[2], bullet[3])

        if bullet[0] > W or bullet[0] + BULLET_W < 0 or bullet[1] + BULLET_H < 0 or bullet[1] > H:
            bullets.pop(i)

            

    # print(len(bullets))


def check_collisions(player, old_player):

    new_x = player["x"]
    new_y = player["y"]
    
    collide = False

    rotated_tank, tank_rect = rotate_center(TANK, (player["x"], player["y"]), player["angle"])
    tank_mask = pygame.mask.from_surface(rotated_tank)

    screen_mask = pygame.mask.Mask((W, H), True)

    #screen collision

    offset = (int(-tank_rect[0]), int(-tank_rect[1]))
    no_bit = tank_mask.overlap_area(screen_mask, offset)

    if no_bit < 840: #number of pixels in tank img is 860ish
        collide = True

    #BOX COLLISION
    for box in boxes:

        box_mask = pygame.mask.from_surface(BOXES[box[2]])

        #check rectangular collision before mask
        if new_y + TANK_H > box[1] and new_y < box[1] + BOX_H[box[2]]:
            if new_x + TANK_W > box[0] and new_x < box[0] + BOX_W[box[2]]:

                offset = (int(box[0] - tank_rect[0]), int(box[1] - tank_rect[1]))

                poi = tank_mask.overlap(box_mask, offset)

                if poi != None:
                    # print("collide")
                    collide = True
    
    if collide:
        player["velocity"] = -player["velocity"]
        player["angle"] = old_player["angle"]
        player["x"] = old_player["x"]
        player["y"] = old_player["y"]

    for bullet in bullets:

        hit = False

        rotated_bullet, bullet_rect = rotate_center(BULLET, (bullet[0], bullet[1]), bullet[2])
        bullet_mask = pygame.mask.from_surface(rotated_bullet)

        offset = (int(bullet_rect[0] - tank_rect[0]), int(bullet_rect[1] - tank_rect[1]))

        poi = tank_mask.overlap(bullet_mask, offset)

        if poi != None:
            #print("hit")
            player["health"] -= 1

            hit = True
        
        for box in boxes:

            box_mask = pygame.mask.from_surface(BOXES[box[2]])

            #check rectangular collision before mask
            if bullet_rect[1] + bullet_rect[3] > box[1] and bullet_rect[1] < box[1] + BOX_H[box[2]]:
                if bullet_rect[0] + bullet_rect[3] > box[0] and bullet_rect[0] < box[0] + BOX_W[box[2]]:

                    offset = (int(box[0] - bullet_rect[0]), int(box[1] - bullet_rect[1]))

                    poi = tank_mask.overlap(box_mask, offset)

                    if poi != None:
                        hit = True
                        boxes.pop(boxes.index(box))

        if hit:
            try:
                bullets.pop(bullets.index(bullet))
            except:
                print("[GAME] Error deleteing bullet")


def reset(current_id, name, conn):

    global connections, players, boxes, bullets, start, _id

    if players[current_id]["health"] > 0:

        print(f"[SERVER] Server reset called by {name}")

        #global variable reset
        players = {}
        boxes = []
        bullets = []
        connections = 0
        _id = 0
        start = False

    #player variable reset
    x, y, angle = get_start_position(players)
    fired = False
    vel = 0
    health = 10
    ready = False

    players[current_id] = {"x":x, "y":y, "angle":angle, "fired":fired, "velocity":vel, "health":health, "name":name, "ready":ready} 

    create_boxes(boxes, random.randint(100, 150))
    print("LENGTH OF BOXES:", len(boxes))

    print("[GAME] Setting up level")
    print("[SERVER] Waiting for a connection, Server Started")

    setup = boxes, players, bullets, start
    send_data(conn, setup)



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

    #print(len(serialized_data))


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

        try:
            command, data = receive_data(conn)            
            
            if not data:
                break

            if command == "":

                if start and players[current_id]["health"] == 0:
                    pass

                elif start:

                    check_collisions(data, players[current_id])
                    
                    if players[current_id]["fired"]:
                        create_bullet(data)
                    
                    move_bullets()
                
                players[current_id] = data

                #engame condition
                    
                
                if len(boxes) < 50:
                    print("[GAME] Generating more boxes")
                    create_boxes(boxes, random.randrange(50, 100))
                
            
            elif command == "ready":
                if len(players) > 1:
                    ready_up(players, connections)
                players[current_id] = data

            elif command == "reset":
                reset(current_id, name, conn)

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
    try:
        del players[current_id]
    except:
        pass
    conn.close()



#MAINLOOP

#setup level with boxes
create_boxes(boxes, random.randint(100, 150))
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
    