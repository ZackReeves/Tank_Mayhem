from utils import scale_image, rotate_center
import pygame

BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.20, 0.10)
TANK = scale_image(pygame.image.load("img/tank.png"), 0.19, 0.19)
BOX = scale_image(pygame.image.load("img/logs.png"), 2,2)

tank_mask = pygame.mask.from_surface(TANK)
box_mask = pygame.mask.from_surface(BOX)

no_bits = box_mask.overlap_area(tank_mask, (15,25))

#print(no_bits)

players = {}

players[1] = {"x":5, "y":5, "angle":5, "fired":False, "velocity":0, "health":7, "name":'john', "ready":False}
players[2] = {"x":5, "y":5, "angle":5, "fired":False, "velocity":0, "health":5, "name":'zack', "ready":False} 

sort_players = list(reversed(sorted(players, key=lambda x: players[x]["health"])))

#for id in sort_players:
    #print(players[id])

print(len(players))


x = BOX.get_width()
y = BOX.get_height()

a = 5
b = 5
w = 10
h = 10

rect = pygame.Rect(a, b, w, h)

centerx = rect[0]

#print(centerx)

SCREEN = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Tanks")

while True:

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(BOX, (50,50))
    SCREEN.blit(TANK, (65,75))
    
    
    pygame.display.update()

