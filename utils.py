import pygame

def scale_image(img, x_factor, y_factor):
    size = round(img.get_width()*x_factor), round(img.get_height()*y_factor)
    return pygame.transform.scale(img,size)

def rotate_center(image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    return rotated_image, new_rect