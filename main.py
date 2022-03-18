#imports
import pygame
import math

from network import Network
from utils import scale_image, rotate_center

pygame.font.init()

#constants

TANKS = [scale_image(pygame.image.load("img/tank_red.png"), 0.19, 0.19), scale_image(pygame.image.load("img/tank_blue.png"), 0.19, 0.19), scale_image(pygame.image.load("img/tank_green.png"), 0.19, 0.19), scale_image(pygame.image.load("img/tank_yellow.png"), 0.19, 0.19), scale_image(pygame.image.load("img/tank_magenta.png"), 0.19, 0.19), scale_image(pygame.image.load("img/tank_cyan.png"), 0.19, 0.19)]
BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.20, 0.10)
BOXES = [scale_image(pygame.image.load("img/logs.png"), 0.66, 0.81), scale_image(pygame.image.load("img/barrel.png"), 0.66, 0.81), scale_image(pygame.image.load("img/tree.png"), 0.66, 0.81), scale_image(pygame.image.load("img/snowman.png"), 0.66, 0.81)]
GRAVE = scale_image(pygame.image.load("img/grave.png"), 0.66, 0.81)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

TANK_W = TANKS[0].get_width()
TANK_H = TANKS[0].get_height()

ROTATION_VEL = 1
MAX_VEL = 2
ACCELERATION = 0.05

FIRE_RATE = 10

#dynamic variables
boxes = []
players = {}
bullets = []
start = False


def redraw_game(boxes, players, bullets, start, current_id):

    global SCREEN

    #fill screen
    SCREEN.fill(WHITE)

    #draw boxes
    for box in boxes:
        SCREEN.blit(BOXES[box[2]], (box[0], box[1]))

    for bullet in bullets:
        rotated_bullet, bullet_rect = rotate_center(BULLET, (bullet[0], bullet[1]), bullet[2])
        SCREEN.blit(rotated_bullet, bullet_rect.topleft)
    
    alive =  []
    count = 0

    title = TIME_FONT.render("Scoreboard", 1, BLACK)
    scoreboard_y = 25
    scoreboard_x = SCREEN_WIDTH - title.get_width() - 10

    sort_players = list(reversed(sorted(players, key=lambda x: players[x]["health"])))

    for id in sort_players:

        player = players[id]
        
        #draw players and check alive
        if player["health"] > 0:

            alive.append(player["name"])
            img = TANKS[id % 6]
            angle = player["angle"]
            
        else:

            img = GRAVE
            angle = 0
        
        rotated_tank, tank_rect = rotate_center(img, (player["x"], player["y"]), angle)
        SCREEN.blit(rotated_tank, tank_rect.topleft)
        
        #draw players in scoreboard
        count += 1
        name = player["name"]
        health = str(player["health"])
        score = name + ": " + str(health)
        text = SCORE_FONT.render(score, 1, BLACK)
        SCREEN.blit(text, (scoreboard_x, scoreboard_y + count*20))

        #check start
        if not start:
            color = RED
            if player["ready"]:
                color = GREEN
            name = NAME_FONT.render(player["name"], 1, color)
            x = player["x"]
            y = player["y"] - name.get_height() - 10
            SCREEN.blit(name, (x, y))            

    #draw scoreboard
    SCREEN.blit(title, (scoreboard_x, 5))
    
    #draw win msg
    if start and len(alive) == 1:
        string = "Game Over, " + str(alive[0]) + " wins!! Resetting in 3 Seconds!"
        colour = GREEN

    #draw death msg
    elif start and players[current_id]["health"] == 0:
        string = "You Died!!"
        colour = RED

    #draw start msg        
    elif not start:
        string = "Press SPACE to Ready Up!!"
        colour = RED
    
    else:
        string = ""
        colour = RED

    

    text = TIME_FONT.render(string, 1, colour)
    SCREEN.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()))

def reset(server, name, ip, player):
    
    global boxes, players, bullets, start

    #server.disconnect()
    command = "reset"
    data = command, name
    server.send_data(data)
    pygame.time.wait(3000)

    

    SCREEN.fill(WHITE)
    pygame.display.update()

    boxes, players, bullets, start = server.receive_data()
    

    game_loop(name, ip)


def game_loop(name, ip):

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

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                
        SCREEN.fill(WHITE)
        text = TIME_FONT.render("Waiting For Server", 1, RED)
        SCREEN.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()))
        pygame.display.update()

        if counter == fps:
            try:
                current_id = server.connect(name, ip)
                break
            except:
                counter = 0
            


    
    boxes, players, bullets, start = server.receive_data()

     
    while run:

        clock.tick(fps)
        player = players[current_id]

        command = ""

        keys = pygame.key.get_pressed()            


        if start and player["health"] > 0:

            moved = False
            player["fired"] = False

            fire_cooldown = max(fire_cooldown - 1, 0)

            if keys[pygame.K_LEFT]:
                player["angle"] += ROTATION_VEL

            if keys[pygame.K_RIGHT]:
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

        elif start and player["health"] == 0:
            pass

        
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
        

        redraw_game(boxes, players, bullets, start, current_id)
        pygame.display.update()

        #check endgame
        alive = 0

        for p in players:
            if players[p]["health"] > 0:
                alive += 1         

        if start and alive == 1:
            reset(server, name, ip, player)


    server.disconnect()
    pygame.quit()
    quit()


#get name
while True:
    error = ""
    ip = input("Please enter the IP of the server: ")
    a = ip.split('.')
    if len(a) == 4:
        for x in a:
            if x.isdigit() and 0 <= int(x) <= 255:
                pass
            else:
                error = "Error, this IP is not allowed (segments must be between 0 and 255)"
    else:
        error = "Error, this IP is not allowed (must contain 4 segments)"

    if error == "":
        break
    else:
        print(error)
        
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
game_loop(name, ip)
