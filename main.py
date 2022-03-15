#imports
import pygame
import math

from network import Network
from utils import scale_image, rotate_center

pygame.font.init()

#constants

TANK = scale_image(pygame.image.load("img/tank.png"), 0.19, 0.19)
BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.20, 0.10)
BOX = scale_image(pygame.image.load("img/box.png"), 0.66, 0.81)  #25 36

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

BOX_W = TANK.get_width()
BOX_H = TANK.get_height()

TANK_W = TANK.get_width()
TANK_H = TANK.get_height()

ROTATION_VEL = 1
MAX_VEL = 5
ACCELERATION = 0.05

FIRE_RATE = 30

#dynamic variables
boxes = []
players = {}
bullets = []
start = False


def redraw_game(boxes, players, bullets, start):

    #global SCREEN

    #fill screen
    SCREEN.fill(WHITE)

    #draw boxes
    for box in boxes:
        SCREEN.blit(BOX, (box[0], box[1]))

        # pygame.draw.rect(SCREEN, RED, pygame.Rect(box[0], box[1], BOX_W, BOX_H))

    for bullet in bullets:
        rotated_bullet, bullet_rect = rotate_center(BULLET, (bullet[0], bullet[1]), bullet[2])
        SCREEN.blit(rotated_bullet, bullet_rect.topleft)

    #draw players
    for player in players:
        p = players[player]
        # pygame.draw.rect(SCREEN, GREEN, pygame.Rect(p["x"], p["y"], TANK_W, TANK_H))
        rotated_tank, tank_rect = rotate_center(TANK, (p["x"], p["y"]), p["angle"])
        SCREEN.blit(rotated_tank, tank_rect.topleft)

    #draw scoreboard
    sort_players = list(reversed(sorted(players, key=lambda x: players[x]["health"])))
    title = TIME_FONT.render("Scoreboard", 1, BLACK)
    start_y = 25
    x = SCREEN_WIDTH - title.get_width() - 10
    SCREEN.blit(title, (x, 5))

    count = 0
    for player in sort_players:
        p = players[player]
        count += 1
        name = p["name"]
        health = str(p["health"])
        score = name + ": " + str(health)
        text = SCORE_FONT.render(score, 1, BLACK)
        SCREEN.blit(text, (x, start_y + count*20))

    #draw start features
    if not start:
        for player in players:
            p = players[player]
            color = RED
            if p["ready"]:
                color = GREEN
            name = NAME_FONT.render(p["name"], 1, color)
            x = p["x"]
            y = p["y"] - name.get_height() - 10
            SCREEN.blit(name, (x, y))
        
        text = TIME_FONT.render("Press SPACE to Ready Up!!", 1, RED)
        SCREEN.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()))


def game_loop(name):

    global boxes, players, bullets, start

    clock = pygame.time.Clock()
    fps = 30

    run = True

    fire_cooldown = FIRE_RATE

    counter = 0

    #connect to network
    server = Network()

    while True:

        clock.tick(fps)

        counter += 1

        if counter == 30:
            try:
                current_id = server.connect(name)
                break
            except:
                counter = 0

            

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
        SCREEN.fill(WHITE)
        text = TIME_FONT.render("Waiting For Server", 1, RED)
        SCREEN.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()))
        pygame.display.update()


                
    
    boxes, players, bullets, start = server.receive_data()


    #setup clock

     
    while run:

        clock.tick(fps)
        player = players[current_id]

        command = ""

        keys = pygame.key.get_pressed()

        if start:

            moved = False
            player["fired"] = False

            fire_cooldown = max(fire_cooldown - 1, 0)

            # if player["health"] = 0:


            if keys[pygame.K_LEFT]:
                player["angle"] += ROTATION_VEL

            elif keys[pygame.K_RIGHT]:
                player["angle"] -= ROTATION_VEL
            
            if keys[pygame.K_UP]:
                moved = True
                player["velocity"] = min(player["velocity"] + ACCELERATION, MAX_VEL)

            elif keys[pygame.K_DOWN]:
                moved = True
                player["velocity"] = min(player["velocity"] - ACCELERATION, MAX_VEL)
                player["velocity"] = max(player["velocity"] - ACCELERATION, -1*MAX_VEL)

            else:
                if player["velocity"] > 0:
                    player["velocity"] = max(player["velocity"] - ACCELERATION, 0 )
                else:
                    player["velocity"] = min(player["velocity"] + ACCELERATION, 0 )
        
            
            radians = math.radians(player["angle"])
            vertical = math.cos(radians) * player["velocity"]
            horizontal = math.sin(radians) * player["velocity"]

            player["x"] -= horizontal
            player["y"] -= vertical
            
            if keys[pygame.K_SPACE] and fire_cooldown == 0:
                fire_cooldown = FIRE_RATE
                player["fired"] = True

        
        else:
            if keys[pygame.K_SPACE]:
                player["ready"] = True
                
            command = "ready"     
        
        data = command, player
        server.send_data(data)
        boxes, players, bullets, start = server.receive_data()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        

        redraw_game(boxes, players, bullets, start)
        pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()


#get name
while True:
    name = input("Please enter your name: ")
    if 0 < len(name) < 20:
        break
    else:
        print("Error, this name is not allowed (must be between 1 and 19 characters)")

#setup pygame screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tanks")

#start game
game_loop(name)
