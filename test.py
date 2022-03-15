from utils import scale_image, rotate_center
import pygame

BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.20, 0.10)
TANK = scale_image(pygame.image.load("img/tank.png"), 0.19, 0.19)
BOX = scale_image(pygame.image.load("img/box.png"), 0.66, 0.81)

x = BOX.get_width()
y = BOX.get_height()

a = 5
b = 5
w = 10
h = 10

rect = pygame.Rect(a, b, w, h)

centerx = rect[0]

print(centerx)

SCREEN = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Tanks")

while True:

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
    SCREEN.fill((255, 255, 255))
    pygame.display.update()

