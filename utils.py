import pygame

def scale_image(img, x_factor, y_factor):
    size = round(img.get_width()*x_factor), round(img.get_height()*y_factor)
    return pygame.transform.scale(img,size)

def blit_rotate_center(surface, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    surface.blit(rotated_image, new_rect.topleft)