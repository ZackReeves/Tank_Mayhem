import math
import pygame
from utils import scale_image, blit_rotate_center


class Tank():

    def __init__(self, max_vel, rotation_vel, start_pos, img):
        self.x, self.y, self.angle = start_pos
        self.img = img
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.acceleration = 0.05

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.x -= horizontal
        self.y -= vertical

    def reduce_speed(self, braking):
        self.vel = max(self.vel - self.acceleration / braking, 0)
        self.move()


    def draw(self, surface):
        blit_rotate_center(surface, self.img, (self.x, self.y), self.angle)
    
    def control(self):

        keys = pygame.key.get_pressed()

        moved = False

        if keys[pygame.K_LEFT]:
            self.rotate(left=True)
        if keys[pygame.K_RIGHT]:
            self.rotate(right=True)
        if keys[pygame.K_UP]:
            moved = True
            self.move_forward()
        if keys[pygame.K_UP]:
            moved = True
            self.reduce_speed(0.5)
        

        if not moved:
            self.reduce_speed(1)