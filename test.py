from utils import scale_image, blit_rotate_center
import pygame

BULLET = scale_image(pygame.image.load("img/bullet.png"), 0.13, 0.05)
TANK = scale_image(pygame.image.load("img/tank.png"), 0.19, 0.19)

x = BULLET.get_width()
y = BULLET.get_height()


print((x, y))

SCREEN = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Tanks")

while True:
        
    SCREEN.fill((255, 255, 255))
    blit_rotate_center(SCREEN, BULLET, (400, 400), 0)
    blit_rotate_center(SCREEN, TANK, (400, 450), 0)
    pygame.display.update()
