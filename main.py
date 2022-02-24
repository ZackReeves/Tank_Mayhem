import pygame
from tank import Tank
from network import Network
from utils import scale_image, blit_rotate_center

clientNumber = 0

TANK = scale_image(pygame.image.load("img/tank.png"), 0.2)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tanks")

FPS = 30

clock = pygame.time.Clock()


block_size = 20
tank_size = 40

def read_pos(str):
    print("s: " + str)
    str = str.split(",")
    return int(str[0]), int(str[1]), int(str[2])


def make_pos(tup):
    print(tup)
    return str(int(tup[0])) + "," + str(int(tup[1])) + "," + str(int(tup[2]))

def redraw_game(t, t2):

    SCREEN.fill(WHITE)
    t.draw(SCREEN)
    t2.draw(SCREEN)

    pygame.display.update()

def game_loop():
    run = True

    n = Network()
    start_pos = read_pos(n.getPos())
    
    t = Tank(max_vel=2, rotation_vel=1, start_pos=start_pos, img=TANK)
    t2 = Tank(max_vel=2, rotation_vel=1, start_pos=start_pos, img=TANK)
     
 
    while run:

        t2_pos = read_pos(str(n.send(make_pos((t.x, t.y, t.angle)))))
        t2.x = t2_pos[0]
        t2.y = t2_pos[1]
        t2.angle = t2_pos[2]
        print("t2  : x: " + str(t2.x) + "  y: " + str(t2.y) + "  a: " + str(t2.angle))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        t.control()

        redraw_game(t, t2)

        clock.tick(FPS)

    pygame.quit()
    quit()


game_loop()