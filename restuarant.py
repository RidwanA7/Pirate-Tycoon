import pygame
from buildings import Building

class Restaurant(Building):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\istockphoto-1320815200-612x612.jpg")

        self.image = pygame.transform.scale(self.image, (70, 50))

        self.rect = self.image.get_rect(topleft=position)

        self.label = "Restaurant"

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        label_surface = pygame.font.SysFont(None, 36).render(self.label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(self.rect.centerx + cameraX, self.rect.centery + cameraY - 10))
        screen.blit(label_surface, label_rect)

    def update(self):
        pass
