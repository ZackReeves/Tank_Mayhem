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

BULLET_W = BULLET.get_width()
BULLET_H = BULLET.get_height()

BOX_W = []
BOX_H = []

for BOX in BOXES:

    BOX_W.append(BOX.get_width())
    BOX_H.append(BOX.get_height())



ROTATION_VEL = 1
MAX_VEL = 2
ACCELERATION = 0.05

FIRE_RATE = 30

#dynamic variables
boxes = []
players = {}
bullets = []
start = False

def request_data_from_file():
    f = open("data.txt")
    data = f.read()
    data = data.split('<-->')
    if(len(data)==4):
        return float(data[0]), float(data[1]), data[2], data[3]
    else:
        return [0,0,1,1]

def create_bullet(player):

    angle = player["angle"]

    tank_rect = pygame.Rect(player["x"], player["y"], TANK_W, TANK_H)
    
    bullet_rect = pygame.Rect(0, 0, BULLET_W, BULLET_H)

    dist = 0.5*TANK_H + BULLET_H
    radians = math.radians(angle)

    bullet_rect.centerx = tank_rect.centerx - dist * math.sin(radians)
    bullet_rect.centery = tank_rect.centery - dist * math.cos(radians)


    vel = 0.375 * (player["velocity"] + MAX_VEL) + MAX_VEL # normalises to 1 max_vel < vel < 1.5 max_vel

    return (bullet_rect.topleft[0], bullet_rect.topleft[1], angle, vel)

def move_bullets():

    for bullet in bullets: # bullets = [(x, y, a, v), (), ()]

        i = bullets.index(bullet)

        radians = math.radians(bullet[2])

        vertical = math.cos(radians) * bullet[3]
        horizontal = math.sin(radians) * bullet[3]
        
        new_x = bullet[0] - horizontal
        new_y = bullet[1] - vertical

        bullets[i] = (new_x, new_y, bullet[2], bullet[3])

        if bullet[0] > SCREEN_WIDTH or bullet[0] + BULLET_W < 0 or bullet[1] + BULLET_H < 0 or bullet[1] > SCREEN_HEIGHT:
            bullets.pop(i)

def check_collisions(player, old_x, old_y, old_angle, current_id):

    new_x = player["x"]
    new_y = player["y"]
    
    collide = False
    del_box = ()
    del_bullet = ()

    rotated_tank, tank_rect = rotate_center(TANKS[current_id % 6], (new_x, new_y), player["angle"])
    tank_mask = pygame.mask.from_surface(rotated_tank)

    screen_mask = pygame.mask.Mask((SCREEN_WIDTH, SCREEN_WIDTH), True)

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
        player["angle"] = old_angle
        player["x"] = old_x
        player["y"] = old_y

    for bullet in bullets:

        hit = False

        rotated_bullet, bullet_rect = rotate_center(BULLET, (bullet[0], bullet[1]), bullet[2])
        bullet_mask = pygame.mask.from_surface(rotated_bullet)

        for box in boxes:

            box_mask = pygame.mask.from_surface(BOXES[box[2]])

            #check rectangular collision before mask
            if bullet_rect[1] + bullet_rect[3] > box[1] and bullet_rect[1] < box[1] + BOX_H[box[2]]:
                if bullet_rect[0] + bullet_rect[3] > box[0] and bullet_rect[0] < box[0] + BOX_W[box[2]]:

                    offset = (int(box[0] - bullet_rect[0]), int(box[1] - bullet_rect[1]))

                    poi = tank_mask.overlap(box_mask, offset)

                    if poi != None:
                        #print("hit box")
                        hit = True
                        del_box = box

        for id in players:

            rotated_tank, tank_rect = rotate_center(TANKS[id % 6], (players[id]["x"], players[id]["y"]), players[id]["angle"])
            tank_mask = pygame.mask.from_surface(rotated_tank)

            offset = (int(bullet_rect[0] - tank_rect[0]), int(bullet_rect[1] - tank_rect[1]))

            poi = tank_mask.overlap(bullet_mask, offset)

            if poi != None:
                #print("hit")
                hit = True

                if id == current_id:
                    player["health"] -= 1

        if hit:
            del_bullet = bullet

    return player, del_box, del_bullet

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
        string = "Game Over, " + str(alive[0]) + " wins!!"
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


    boxes, players, start = server.receive_data()



    while run:

        clock.tick(fps)
        try:
            x, y, button0, button1 = request_data_from_file()
            fpga = True
        except:
            x, y, buuton0, button1 = 0,0,1,1 
            fpga = False
        
        player = players[current_id]

        command = ""
        del_box = ()
        new_bullet = (0,0,0,0)

        keys = pygame.key.get_pressed()            


        if start:
            if  player["health"] > 0:
                moved = False
                player["fired"] = False

                fire_cooldown = max(fire_cooldown - 1, 0)

                old_x = player["x"]
                old_y = player["y"]
                old_angle = player["angle"]

                if fpga:

                    player["angle"] += ROTATION_VEL*x
                    player["velocity"] = min(player["velocity"] -y*ACCELERATION, MAX_VEL)
                    player["velocity"] = max(player["velocity"] -y*ACCELERATION, -1*MAX_VEL)

                    if button0 == '0' and fire_cooldown == 0:
                        fire_cooldown = FIRE_RATE
                        player["fired"] = True

                else:
                    if keys[pygame.K_LEFT]:
                        player["angle"] += ROTATION_VEL

                    elif keys[pygame.K_RIGHT]:
                        player["angle"] -= ROTATION_VEL
                    
                    if keys[pygame.K_UP]:
                        moved = True
                        player["velocity"] = min(player["velocity"] + ACCELERATION, MAX_VEL)

                    elif keys[pygame.K_DOWN]:
                        moved = True
                        player["velocity"] = max(player["velocity"] - ACCELERATION, -1*MAX_VEL)

                    else:
                        if player["velocity"] > 0:
                            player["velocity"] = max(player["velocity"] - ACCELERATION, 0 )
                        else:
                            player["velocity"] = min(player["velocity"] + ACCELERATION, 0 )

                    if keys[pygame.K_SPACE] and fire_cooldown == 0:
                        fire_cooldown = FIRE_RATE
                        player["fired"] = True
                
                radians = math.radians(player["angle"])
                vertical = math.cos(radians) * player["velocity"]
                horizontal = math.sin(radians) * player["velocity"]

                player["x"] -= horizontal
                player["y"] -= vertical

                if player["fired"]:
                    new_bullet = create_bullet(player)
            
            move_bullets()

            player, del_box, del_bullet = check_collisions(player, old_x, old_y, old_angle, current_id)
            try:
                bullets.pop(bullets.index(del_bullet))
            except:
                pass
        else:
            if fpga:
                if  button0 == '0':
                    player["ready"] = True
            else:
                if keys[pygame.K_SPACE]:
                    player["ready"] = True
                
            command = "ready"     
        
        data = command, player, del_box, new_bullet
        server.send_data(data)

        boxes, players, new_bullets, start = server.receive_data()

        for bullet in new_bullets:
            if new_bullets[bullet] != (0,0,0,0):
                bullets.append(new_bullets[bullet])

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False  
        

        redraw_game(boxes, players, bullets, start, current_id)
        pygame.display.update()

        #check endgame
        alive = 0

        for player in players:
            if players[player]["health"] > 0:
                alive += 1

        
        if start and alive == 1:
            print("Game Over")
            run = False
            pygame.time.wait(1000)
            



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
